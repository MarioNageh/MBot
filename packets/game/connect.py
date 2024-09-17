from client.client import Client
from packets.packet import Packet
from utils.reader import Reader
from utils.writer import Writer


class Connect(Packet):
    @staticmethod
    def packet_processor(reader: Reader, client: Client):
        pass

    PACKET_SIZE = 28
    PACKET_ID = 1052

    def __init__(self, client,account_id):
        super().__init__(client)
        self.account_id = account_id

    def finalize(self):
        writer = Writer(self.PACKET_SIZE, is_game_server_packet=True)
        writer.write_int_in_bytes(self.PACKET_SIZE, 2)
        writer.write_int_in_bytes(self.PACKET_ID, 2)
        writer.write_int_in_bytes(self.account_id, 4)
        writer.write_byte_array(bytes.fromhex("B82200007B00456E00000000000000000A000000"))
        writer.write_string_in_bytes(Packet.packet_signature())
        self.data = writer.get_data()
