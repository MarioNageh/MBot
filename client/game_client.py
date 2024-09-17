from client.client import Client, ClientType
from cryptography.dhe_generator import DHEGenerator
from cryptography.game_cryptography import GameCryptography, BlowfishAlgorithm
from exceptions import UserNotHaveEnoughCps, AStarPathCalculationError, BotBaseException, UserNotHaveThisItem, \
    PlayerNotTeleport
from packets.packet import Packet
from sockets.game_socket import Socket
from utils.reader import Reader
from packets.game import *
from data.player import Player as Heroinfo


class GameClient(Client):
    def __init__(self, socket: Socket, main_app):
        super().__init__(socket, main_app)
        self.key_exchange = False

        self.enc_client = None
        self.server_crypto = GameCryptography(BlowfishAlgorithm.CFB64, self.main_app.configration.blowfish_key)
        # self.server_crypto = GameCryptography(self.main_app.configration.blowfish_key, self)
        self.client_crypto = GameCryptography(BlowfishAlgorithm.CFB64, self.main_app.configration.blowfish_key)
        self.socket.client = self
        self.client_type = ClientType.Game

        ############# Data #############
        self.player: Heroinfo = None

    async def exchange_key(self, packet: Reader):
        self.key_exchange = True

        serverDHK = ServerDiffieHellmanPacket(self)
        serverDHK.packet_processor(packet, self)
        client_keys = DHEGenerator(serverDHK.p_int, serverDHK.g_int)

        client_dh_packet = bytearray()
        client_dh_packet.extend(bytes.fromhex(
            "35e98c41bb8d0aa20000000e000000040df0bd7994ac75e8b33491300b80000000"))

        public_key_str = hex(client_keys.get_public_key()).lstrip('0x').upper()
        client_dh_packet.extend(public_key_str.encode('utf-8'))
        client_dh_packet.extend(Packet.packet_signature().encode('utf-8'))

        shared_key = client_keys.compute_key(serverDHK.public_key_int)
        key_bytes = shared_key.to_bytes(64, byteorder='big')

        client_crypto = GameCryptography(BlowfishAlgorithm.CFB64, key_bytes, iv_one=serverDHK.iv_one,
                                         iv_two=serverDHK.iv_two)

        server_crypto = GameCryptography(BlowfishAlgorithm.CFB64, key_bytes, iv_one=serverDHK.iv_two,
                                         iv_two=serverDHK.iv_one)

        await self.send(client_dh_packet, send_immediately=True)

        self.client_crypto = client_crypto
        self.server_crypto = server_crypto
        connect_packet = Connect(self, self.main_app.auth_client.forward_packet.account_id)
        await self.send(connect_packet)

        self.main_app.is_fully_connected = True

    def error_handler(self, exception: Exception):
        if isinstance(exception, BotBaseException):
            self.main_app.re_login = exception.re_login
            self.main_app.printer.print_fail(exception.message)
        else:
            self.main_app.printer.print_fail(str(exception))
        if (isinstance(exception, UserNotHaveEnoughCps) or
                isinstance(exception, AStarPathCalculationError)
            or isinstance(exception, UserNotHaveThisItem)
            or isinstance(exception, PlayerNotTeleport)
        ):
            exp: BotBaseException = exception

            if not exp.re_login:
                self.main_app.processor.running = False

            self.main_app.kernel.stop()
            self.main_app.is_fully_connected = False
            self.socket.close_socket()
            return
        else:
            raise exception

    async def on_finish_process(self, packet):
        try:
            # print(packet)
            if not self.key_exchange:
                await self.exchange_key(packet)
            else:
                pass
        except Exception as e:
            raise e
