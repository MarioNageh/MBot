import asyncio
import enum
import socket
import threading
import time
from typing import Callable, Awaitable, TYPE_CHECKING

if TYPE_CHECKING:
    from client.client import Client


class SocketType(enum.Enum):
    GameServer = 1
    AccountServer = 2
    EncServer = 3


class Socket:

    def __init__(self, socket_type: SocketType, ip: str,
                 port: int,
                 on_receive: Callable[['Client', bytearray], Awaitable[None]],
                 on_disconnect: Callable[[SocketType, object], Awaitable[None]],
                 on_connect: Callable[[SocketType, str, int], Awaitable[None]],
                 main_app=None):
        self._socket_type = socket_type
        self._buffer_size = 1024 * 8  # 8Kb
        self.socket_sleep_time = 1 / 1000  # 1 Mill

        self.on_receive = on_receive
        self.on_disconnect = on_disconnect
        self.on_connect = on_connect
        self.ip = ip
        self.port = port

        self._reader = None
        self._writer = None

        self._socket_state = False
        self.client = None

        self.main_app = main_app
        self.last_received_time = time.time()

    async def connect(self):
        try:
            self._reader, self._writer = await asyncio.open_connection(self.ip, self.port)
            await self.on_connect(self._socket_type, self.ip, self.port)
            self._socket_state = True
        except ConnectionRefusedError:
            print(f"Connection to server at {self.ip}:{self.port} refused")
            return False
        return True

    async def close_socket(self):
        if not self._socket_state:
            return
        self._socket_state = False
        self._writer.close()
        await self.on_disconnect(self._socket_type, self.client)

    async def send(self, data: bytes):
        if not self._socket_state:
            return
        self._writer.write(data)
        await self._writer.drain()

    async def receive(self):
        try:
            while self._socket_state:
                read_task = asyncio.create_task(self._reader.read(self._buffer_size))
                self.main_app.tasks.append(read_task)

                data_received = await read_task
                if len(data_received) == 0:
                    self.main_app.printer.print_fail(f"Received empty data from {self._socket_type}")
                    await self.close_socket()
                    break

                self.last_received_time = time.time()
                await self.on_receive(self.client, data_received)
        except ConnectionResetError:
            await self.close_socket()
        finally:
            if not self._socket_state:
                return
            self._writer.close()
            await self._writer.wait_closed()

    async def start_receive(self):
        # Connect to the server
        is_connected = self._socket_state
        if not self._socket_state:
            is_connected = await self.connect()

        if not is_connected:
            return
        # Start receiving data
        task = asyncio.create_task(self.receive())

        await self.main_app.add_task_to_event_loop(task)

    def get_socket_state(self):
        return self._socket_state
