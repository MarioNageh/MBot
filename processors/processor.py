import enum
import time
from collections import deque
from threading import Thread

from exceptions import BotBaseException
from utils.helpers import to_hex_string


class ProcessorTaskType(enum.Enum):
    Send = 1
    Receive = 2
    ReceiveIncomplete = 3


class ProcessorTask:

    def __init__(self, task_type: ProcessorTaskType, data, client) -> None:
        self.data = data
        self.client = client
        self.task_type = task_type
        self.task_id = 0

    def __str__(self):
        return f"{to_hex_string(self.data)}"


class Handlers:
    process_packet_handler = {}

    @staticmethod
    def register_packet_handler(packet_id, client_type):
        def decorator(func):
            if client_type not in Handlers.process_packet_handler:
                Handlers.process_packet_handler[client_type] = {}
            Handlers.process_packet_handler[client_type][packet_id] = func
            return func

        return decorator

    @staticmethod
    def get_packet_handler(packet_id, client_type):
        try:
            return Handlers.process_packet_handler[client_type][packet_id]
        except KeyError:
            return None


class Processor:
    def __init__(self, kernel) -> None:
        self.received_tasks: [ProcessorTask] = deque()
        self.send_tasks: [ProcessorTask] = deque()
        self.incomplete_tasks: [ProcessorTask] = deque()
        self.running = True
        self.kernel = kernel
        self.thread = Thread(target=self.main_event,name="Processor")
        self.thread.start()

    def enqueue(self, task: ProcessorTask):
        print(f"Enqueue {task}")
        if task.task_type == ProcessorTaskType.Receive:
            self.received_tasks.append(task)
        elif task.task_type == ProcessorTaskType.Send:
            self.send_tasks.append(task)
        elif task.task_type == ProcessorTaskType.ReceiveIncomplete:
            self.incomplete_tasks.append(task)

    def main_event(self):
        while self.running:
            self.deque()
            time.sleep(0.05)

    def deque(self):
        # deque the received tasks first
        while len(self.received_tasks) > 0:
            needs_to_decrypt = True
            task: ProcessorTask = self.received_tasks.popleft()
            '''
            here we have case that we received incomplete packet before and we need to check if we have the rest of the packet
            '''
            if len(self.incomplete_tasks) > 0:
                '''
                first decrypt the data and append it to the last incomplete task
                '''
                last_incomplete_task: ProcessorTask = self.incomplete_tasks.popleft()
                task.client.decrypt_server_packet(task.data)
                last_incomplete_task.data += task.data
                task = last_incomplete_task
                needs_to_decrypt = False

            try:
                for packet in task.client.packet_handler(task.data, needs_to_decrypt):
                    task.client.on_finish_process(packet)
            except Exception as e:
                task.client.error_handler(e)

        # deque the send tasks
        while len(self.send_tasks) > 0:
            task: ProcessorTask = self.send_tasks.popleft()
            if task.client.socket.get_socket_state():
                task.client.socket.get_socket().send(task.data)

        try:
            self.kernel.execute_events()
        except Exception as e:
            if isinstance(e, BotBaseException):
                e.client.error_handler(e)
            else:
                raise e
