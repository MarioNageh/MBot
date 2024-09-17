import time
from time import sleep
from typing import Optional, TYPE_CHECKING

from client.client import Client
from client.auth_client import AuthClient
from configration import Config
from packets.auth import Login
from processors.kernel import Kernel
from sockets.as_game_socket import SocketType
from sockets.as_game_socket import Socket
from threads.astar_cals import AStarWorkerThread
from threads.main_thread import MBotMainThread
from utils.printer import TerminalPrinter, PrinterData
from processors.async_processor import AsyncProcessor, ProcessorTask, ProcessorTaskType

if TYPE_CHECKING:
    pass


class Mbot:
    def __init__(self, user_name: str, password: str, server_name: str):
        self.printer: TerminalPrinter = TerminalPrinter(PrinterData(user_name="Not Login", user_id=user_name))
        self.configration: Config = Config()
        self.number_of_login_attempts = 0
        self.is_fully_connected = False
        self.user_name = user_name
        self.password = password
        self.server_name = server_name
        self.kernel = Kernel()
        self.processor = AsyncProcessor(self.kernel, self)

        self.auth_socket: Optional[Socket] = None
        self.auth_client = None

        self.game_client = None
        self.game_socket: Optional[Socket] = None
        self.map = None
        self._is_fully_connected = False
        self.auth_server_connected = False
        self.auth_server_connected_time = 0

        self.forward_done = False
        self.re_login = True

        self._stop_event = asyncio.Event()
        self.tasks = []

    async def on_receive(self, client: 'Client', data):
        task = ProcessorTask(ProcessorTaskType.Receive, bytearray(data), client)
        self.processor.enqueue(task)

    async def on_disconnect(self, socket_type, client):
        self.printer.print_fail(f"Disconnected from {socket_type}")
        if socket_type == SocketType.GameServer:
            self._stop_event.set()

    async def on_connect(self, socket_type: SocketType, ip: str, port: int):
        self.printer.print_success(f"Connected to {socket_type} xxx.xxx.xxx.xxx:xxx")

    async def login(self):
        self.printer.print_info(f"Connecting to the server [auth] with {self.user_name}")
        self.processor.stop()
        await self.cleanup_tasks()

        try:

            main_event_task = asyncio.create_task(self.processor.main_event())
            await asyncio.sleep(0)  # high priority
            self.tasks.append(main_event_task)

            self.game_client = None
            self.game_socket = None
            self._is_fully_connected = False
            self.auth_server_connected = False
            self.auth_server_connected_time = 0
            self.auth_server_start_time = time.time()
            self.number_of_login_attempts += 1
            self.processor.incomplete_tasks.clear()
            self.processor.received_tasks.clear()
            self.processor.send_tasks.clear()
            self.kernel.stop()
            self.kernel.start()

            self.auth_socket: Socket = Socket(SocketType.AccountServer,
                                              self.configration.game_ip,
                                              self.configration.game_port,
                                              self.on_receive,
                                              self.on_disconnect,
                                              self.on_connect,
                                              self)
            await self.auth_socket.connect()

            self.auth_client = AuthClient(self.auth_socket, self)
            await self.auth_client.start_client()

            login_packet = Login(self.auth_client, self.user_name, self.password, self.server_name)
            await self.auth_client.send(login_packet, send_immediately=True)

            await self._stop_event.wait()

        except asyncio.CancelledError:
            self.printer.print_info("Login process was cancelled.")
            raise
        except Exception as e:
            self.printer.print_info(f"Exception during login: {e}")
            raise
        finally:
            self.printer.print_info("Cleaning up login process...")
            self._stop_event.clear()
            self.processor.stop()
            await self.cleanup_tasks()

    async def cleanup_tasks(self):
        if not self.tasks:
            return

        # Attempt to cancel each task
        for task in self.tasks:
            task.cancel()

        # Wait for all tasks to either be cancelled or completed
        self.printer.print_info(f"Waiting for Tasks len: {len(self.tasks)} to be cancelled")
        done, pending = await asyncio.wait(self.tasks, return_when=asyncio.ALL_COMPLETED)
        self.printer.print_info(f"Tasks done: {len(done)} pending: {len(pending)}")
        for task in done:
            try:
                await task
            except asyncio.CancelledError:
                self.printer.print_info("Task was cancelled.")
            except Exception as e:
                self.printer.print_fail(f"Error in task: {e}")

        self.tasks.clear()
        self._stop_event.clear()

    async def add_task_to_event_loop(self, task):
        self.tasks.append(task)

    async def add_awaitable_to_event_loop(self, awaitable):
        task = asyncio.create_task(awaitable)
        self.tasks.append(task)
        return await task

    def connection_with_auth_server_timeout(self):
        return self.auth_server_connected and time.time() - self.auth_server_connected_time > 60

    def connection_with_game_server_timeout(self):
        if not self.game_socket:
            return False
        soc: Socket = self.game_socket
        last_received_diff = time.time() - soc.last_received_time
        if not soc.get_socket_state() or last_received_diff > 60:
            return False
        return True


main_thread = None


async def main():
    seed_id = 74330
    bots = []
    tasks = []
    for i in range(seed_id, seed_id + 150):
        mbot = Mbot(f"{i}", "etyumhsgfhs", Config.server_name())
        main_thread.add_bot(mbot)
        bots.append(mbot)
        task = asyncio.create_task(mbot.login())
        tasks.append(task)
        if (i - seed_id + 1) % 30 == 0:
            await asyncio.sleep(10)

    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    import asyncio

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        main_thread = MBotMainThread("BaseBot Thread", event_loop=loop)

        astar_thread = AStarWorkerThread("Astar Thread", 5)
        while not astar_thread.all_processes_ready():
            sleep(.5)
        loop.create_task(main())
        loop.run_forever()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
