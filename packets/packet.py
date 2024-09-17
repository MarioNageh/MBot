from abc import ABC, abstractmethod

from client.client import Client
from utils.reader import Reader


class Packet(ABC):
    def __init__(self, client: Client):
        self.packet_size = 0
        self.packet_packet_id = 0
        self.reader = None
        self.data = None
        self.client: Client = client
        self.client_type = client.client_type

    def decode_packet(self, data):
        self.data = data
        self.reader = Reader(data)
        self.packet_size = self.reader.read_int_16()
        self.packet_packet_id = self.reader.read_int_16()
        # self.packet_processor(data)

    def set_packet_buffer(self, reader: Reader):
        self.reader = reader
        self.data = reader._buffer

    @staticmethod
    async def packet_action(data):
        pass

    @staticmethod
    @abstractmethod
    async def packet_processor(reader: Reader, client):
        pass

    @abstractmethod
    def finalize(self):
        pass

    def to_hex_string(self):
        return (''.join(' {:02x}'.format(x) for x in self.data))[1::]

    def __str__(self) -> str:
        return self.to_hex_string()

    @staticmethod
    def packet_signature() -> str:
        return "TQClient"
        return "engwalid"
        return "TQClient"

    def print_row_packet(self):
        if self.data is None:
            return
        rd = Reader(self.data)
        rd.read_int_16()
        print(f"Packet Id [{rd.read_int_16()}]")
        print(self.to_hex_string())
