import enum
import socket
import threading
import time
from typing import Callable


class SocketType(enum.Enum):
    GameServer = 1
    AccountServer = 2
    EncServer = 3


class Socket(threading.Thread):

    def __init__(self, socket_type: SocketType, ip: str,
                 port: int,
                 on_receive: Callable[[object, bytearray], None],
                 on_disconnect: Callable[[SocketType, object], None],
                 on_connect: Callable[[SocketType, str,int], None],
                 main_app=None):

        super(Socket, self).__init__(name=f"{socket_type} For {main_app.user_name}")
        self._socket_type = socket_type
        self._buffer_size = 1024 * 8  # 8Kb
        self.socket_sleep_time = 1 / 1000  # 1 Mill

        self.on_receive = on_receive
        self.on_disconnect = on_disconnect
        self.on_connect = on_connect
        self.ip = ip
        self.port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


        self.client = None
        self.main_app = main_app
        self._socket_state = True
        self.last_received_time = time.time()

    def get_socket_type(self):
        return self._socket_type

    def get_socket_state(self):
        self.main_app.lock.acquire()
        socket_state = self._socket_state
        self.main_app.lock.release()
        return socket_state

    def close_socket(self):
        if not self._socket_state:
            return
        self.main_app.printer.print_fail("Received 0 Data Connection Closed")
        self._socket_state = False
        self._socket.close()
        self.on_disconnect(self.get_socket_type(), self.client)

    def start_receive(self):
        self._socket.connect((self.ip, self.port))
        self.on_connect(self._socket_type, self.ip, self.port)
        self.start()

    def run(self):
        self.main_app.printer.print_info(f"Start Receive {self._socket_type}\n")
        if self._socket_type == SocketType.EncServer:
            pass
        else:
            while self._socket_state:
                try:
                    data_received = self._socket.recv(self._buffer_size)

                    if len(data_received) == 0:
                        self.close_socket()
                        break
                    self.last_received_time = time.time()
                    self.on_receive(self.client, bytearray(data_received))
                except socket.error as e:
                    if not self._socket_state:
                        break
                    self.close_socket()
                    print(f"Error: {e}")
                    self.on_disconnect(self._socket_type, self.client)
                    break
                time.sleep(self.socket_sleep_time)

    def receive(self):
        data_received = self._socket.recv(self._buffer_size)
        return data_received

    def get_socket(self):
        return self._socket
