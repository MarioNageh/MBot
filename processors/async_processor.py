import asyncio
import enum
from collections import deque
from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from client.client import Client
    from processors.kernel import Kernel
    from packets.packet import Packet
    from async_main import Mbot

class ProcessorTaskType(enum.Enum):
    Send = 1
    Receive = 2
    ReceiveIncomplete = 3


class ProcessorTask:
    def __init__(self, task_type: ProcessorTaskType, data, client) -> None:
        self.data = data
        self.client = client
        self.task_type = task_type

    def __str__(self):
        return f"Task({self.task_type}, {len(self.data)} bytes)"


class Handlers:
    process_packet_handler = {}

    @staticmethod
    def async_register_packet_handler(packet_id, client_type):
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


class AsyncProcessor:
    def __init__(self, kernel, mbot: 'Mbot') -> None:
        self.received_tasks: [ProcessorTask] = deque()
        self.send_tasks: [ProcessorTask] = deque()
        self.incomplete_tasks: [ProcessorTask] = deque()
        self.running = True
        self.kernel: Kernel = kernel
        self.loop = asyncio.get_event_loop()
        self.mbot: Mbot = mbot
        self.is_started = False

    def enqueue(self, task: ProcessorTask):
        if task.task_type == ProcessorTaskType.Receive:
            self.received_tasks.append(task)
        elif task.task_type == ProcessorTaskType.Send:
            self.send_tasks.append(task)
        elif task.task_type == ProcessorTaskType.ReceiveIncomplete:
            self.incomplete_tasks.append(task)

    def stop(self):
        self.running = False
        self.is_started = False
        self.received_tasks.clear()
        self.send_tasks.clear()
        self.incomplete_tasks.clear()
        self.kernel.stop()
        self.mbot.printer.print_info("Processor stopped.")


    async def main_event(self):
        self.mbot.printer.print_info("Processor started.")
        self.is_started = True
        self.running = True
        while self.running:
            await self.process_tasks()
            await asyncio.sleep(0)

    async def process_tasks(self):
        # Process received tasks
        while self.received_tasks:
            task = self.received_tasks.popleft()
            await self.process_task(task)

        # Process send tasks
        while self.send_tasks:
            task = self.send_tasks.popleft()
            await self.send_data(task)

        # Handle other kernel tasks
        await self.kernel.execute_events()

    async def process_task(self, task: ProcessorTask):
        needs_to_decrypt = True
        client: 'Client' = task.client
        if self.incomplete_tasks:
            incomplete_task = self.incomplete_tasks.popleft()
            task.client.decrypt_server_packet(task.data)
            incomplete_task.data += task.data
            task = incomplete_task
            needs_to_decrypt = False

        # Process packet
        try:
            async for packet in client.packet_handler(task.data, needs_to_decrypt):
                await task.client.on_finish_process(packet)
        except Exception as e:
            await task.client.error_handler(e)

    async def send_data(self, task: ProcessorTask):
        try:
            await task.client.socket.send(task.data)
        except Exception as e:
            await task.client.error_handler(e)
