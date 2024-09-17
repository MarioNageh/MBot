import json
import threading
import time
from time import sleep
from typing import Optional

from client.auth_client import AuthClient
from exceptions import UserNotHaveThisItem

from packets.auth.login import Login
from processors.kernel import Kernel
from processors.processor import (Processor,
                                  ProcessorTask, ProcessorTaskType)
from threads.astar_cals import AStarWorkerThread
from threads.main_thread import MBotMainThread
from configration import Config
from sockets.game_socket import Socket, SocketType
from utils.map import Map
from utils.printer import TerminalPrinter, PrinterData


class Mbot:
    def __init__(self, user_name: str, password: str, server_name: str):
        self.printer: TerminalPrinter = TerminalPrinter(PrinterData(user_name="Not Login", user_id=user_name))
        self.lock = threading.Lock()
        self.configration: Config = Config()
        self.number_of_login_attempts = 0
        self.is_fully_connected = False
        self.user_name = user_name
        self.password = password
        self.server_name = server_name
        self.kernel = Kernel()
        self.processor = Processor(self.kernel)
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

    def login(self):
        try:
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

            self.auth_client = AuthClient(self.auth_socket, self)
            login_packet = Login(self.auth_client, self.user_name, self.password, self.server_name)
            self.auth_client.send(login_packet, send_immediately=True)
        except ConnectionRefusedError as e:
            self.auth_socket.close_socket()
            self.printer.print_fail("Connection Refused")

    def on_receive(self, client_type, data):
        task = ProcessorTask(ProcessorTaskType.Receive, data, client_type)
        self.processor.enqueue(task)

    def on_disconnect(self, socket_type, client):
        self.printer.print_fail(f"Disconnected from {socket_type}")

    def on_connect(self, socket_type: SocketType, ip: str, port: int):
        self.printer.print_success(f"Connected to {socket_type} {ip}:{port}")

    @property
    def is_fully_connected(self):
        return self.game_socket.get_socket_state() and self._is_fully_connected

    @is_fully_connected.setter
    def is_fully_connected(self, value):
        self._is_fully_connected = value

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



if __name__ == '__main__':

    accounts = json.load(open("accounts.json"))
    main_thread = MBotMainThread("BaseBot Thread")
    astar_thread = AStarWorkerThread("Astar Thread",10)
    while not astar_thread.all_processes_ready():
        sleep(.5)


    for account in range(1, 31):
        try:
            bot = Mbot(f'red{account}', "11231", Config.server_name())
            bot.map = map

            bot.login()
            main_thread.add_bot(bot)

        except Exception as e:
            raise e
