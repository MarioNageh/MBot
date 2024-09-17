import time

from client.client import Client, ClientType
from client.game_client import GameClient
from cryptography.auth_cryptography import AuthCryptography
from exceptions import AccountServerRefuseConnection, BotBaseException
from sockets.as_game_socket import Socket, SocketType
from packets.auth import *


class AuthClient(Client):

    def __init__(self, socket: Socket, main_app):
        super().__init__(socket, main_app)
        self.client_crypto = AuthCryptography(False, True)
        self.server_crypto = AuthCryptography(True, False)
        self.socket.client = self
        self.forward_packet = None
        self.client_type = ClientType.Auth





    async def on_finish_process(self, packet):
        if isinstance(packet, Forward):
            rnd_mac_address = MacAddress.generate_random_mac()
            mac_address_packet = MacAddress(self, packet.account_id, rnd_mac_address)
            await self.send(mac_address_packet, send_immediately=True)
            await self.socket.close_socket()


            self.main_app.auth_server_connected = True
            self.main_app.auth_server_connected_time = time.time()

            self.main_app.game_socket = Socket(SocketType.GameServer,
                                               packet.ip, packet.port, self.main_app.on_receive,
                                               self.main_app.on_disconnect, self.main_app.on_connect, self.main_app)

            game_client = GameClient(self.main_app.game_socket, self.main_app)

            self.main_app.game_client = game_client
            await game_client.start_client()

            self.main_app.forward_done = True

    async def error_handler(self, exception):
        if isinstance(exception, BotBaseException):
            self.main_app.re_login = exception.re_login
            self.main_app.printer.print_fail(exception.message)
        else:
            self.main_app.printer.print_fail(str(exception))

        if isinstance(exception, AccountServerRefuseConnection):
            await self.socket.close_socket()
            self.main_app.auth_server_connected = False
            self.main_app.auth_server_connected_time = 0
