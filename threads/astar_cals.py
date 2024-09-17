import threading
from threading import Thread
from typing import TYPE_CHECKING
from multiprocessing import Process, Queue
from constants import Coordinate
from processors.kernel import Event
from utils.map import Map
from multiprocessing import Manager

if TYPE_CHECKING:
    from client.game_client import GameClient


def process_task(task_queue, result_queue, process_id,number_of_ready_processes):
    """Worker process function"""
    map_for_cals = Map("map.bin")
    number_of_ready_processes.value += 1

    while True:
        try:
            task = task_queue.get()
            print(f"Process {process_id} got task: {task}")
            if task == "STOP":
                break  # Stop the worker process

            start_coords, end_coords, task_id = task
            path = map_for_cals.a_star(
                (start_coords.x, start_coords.y),
                (end_coords.x, end_coords.y)
            )
            result_queue.put((task_id, process_id, path))
        except KeyboardInterrupt as e:
            print(e)



class AStarWorkerThread(Thread):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AStarWorkerThread, cls).__new__(cls)
        return cls._instance

    def __init__(self, name="AstarThread", number_of_processes=1):
        if getattr(self, '_initialized', False):
            return
        self._initialized = True
        Thread.__init__(self, name=name)
        self.running = True
        self.processes = []
        self.number_of_processes = number_of_processes
        self.task_id = 0
        manager = Manager()
        self.call_back_registers = manager.dict()  # Shared dict to store callbacks
        self.result_queue = Queue()
        self.process_queues = []
        self.register_client = {}
        self.number_of_ready_processes = manager.Value('i', 0)
        self.start_workers()
        self.start()
        self.lock = threading.Lock()

    def register_call_back(self, task_id, client: 'GameClient'):
        self.register_client[client.player.user_id] = client
        self.call_back_registers[task_id] = client.player.user_id

    def get_call_back(self, task_id):
        """
        get it from the register and remove it
        """
        user_id = self.call_back_registers.get(task_id)
        return self.register_client.get(user_id)




    def all_processes_ready(self):
        return self.number_of_ready_processes.value == self.number_of_processes

    def start_workers(self):
        """Start worker processes and their respective queues"""
        for i in range(self.number_of_processes):
            q = Queue()
            process = Process(target=process_task, args=(q, self.result_queue, i,self.number_of_ready_processes))
            process.start()
            self.processes.append(process)
            self.process_queues.append(q)
        print(f"Started {self.number_of_processes} A* worker processes")

    def enqueue(self, client_data: 'GameClient', start: Coordinate, end: Coordinate):
        """Enqueue a request and assign it to one of the worker processes"""
        if not self.running:
            print("Shutting down, not accepting new tasks")
            return  # Prevent new tasks from being added during shutdown

        with self.lock:
            process_id = self.task_id % self.number_of_processes
            self.register_call_back(self.task_id, client_data)
            self.process_queues[process_id].put((start, end, self.task_id))
            self.task_id += 1

    def run(self):
        """Main thread loop for processing results from worker processes"""

        print("AstarThread started")
        while self.running:
            try:
                task_id, process_id, path = self.result_queue.get()
                print(f"Got result for task {task_id} from process {process_id}")
                client = self.get_call_back(task_id)
                from processors.events import received_finish_astar
                event: Event = Event.create_event_from_callback(client, received_finish_astar)
                event.event_args["path"] = path
                client.main_app.kernel.add_event(event)
            except Exception as e:
                raise e

        print("AstarThread shutting down...")


    def stop_workers(self):
        """Send stop signals to worker processes and stop them gracefully"""
        self.running = False

        for q in self.process_queues:
            q.put("STOP")  # Send stop signal to each worker process
        for process in self.processes:
            process.join()
        print("All workers stopped")

    def shutdown(self):
        """Gracefully shutdown the worker thread and all processes"""
        print("Initiating graceful shutdown...")
        self.stop_workers()
        self.join()  # Wait for the main thread to finish
        print("Graceful shutdown complete")
