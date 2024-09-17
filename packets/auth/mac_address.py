import random
from abc import ABC

from client.client import Client, ClientType
from packets.packet import Packet
from processors.async_processor import AsyncProcessor, Handlers
from utils.reader import Reader
from utils.writer import Writer


class MacAddress(Packet, ABC):
    PACKET_ID = 1100
    PACKET_SIZE = 52
    CLIENT_TYPE = ClientType.Auth

    def __init__(self, client: Client, account_id: int, mac: str):
        super().__init__(client)
        self.account_id = account_id
        self.mac = mac

    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    def packet_processor(reader: Reader, client):
        return None

    @staticmethod
    def generate_random_mac():
        random_string = ''
        for _ in range(12):
            random_integer = random.randint(0, 255)
            random_string += (chr(random_integer))
        return random_string
    def finalize(self):
        writer = Writer(self.PACKET_SIZE)
        writer.write_int_in_bytes(self.PACKET_SIZE, 2)
        writer.write_int_in_bytes(self.PACKET_ID, 2)
        writer.write_int_in_bytes(self.account_id, 4)
        writer.write_string_in_bytes(self.mac, 12)
        self.data = writer.get_data()
