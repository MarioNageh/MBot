from client.client import Client, ClientType
from packets.packet import Packet
from processors.async_processor import Handlers
from utils.reader import Reader
from utils.writer import Writer


class Tick(Packet):
    PACKET_ID = 1012
    PACKET_SIZE = 32
    CLIENT_TYPE = ClientType.Game

    def __init__(self, client: Client, account_id: int, time_stamp: int, rand_bytes: bytes, enc_name: str):
        super().__init__(client)
        self.account_id = account_id
        self.time_stamp = time_stamp
        self.rand_bytes = rand_bytes
        self.enc_name = enc_name



    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):
        account_id = reader.read_int_32()
        time_stamp = reader.read_int_32()
        rand_bytes = reader.read_bytes(16)
        enc_name = reader.read_bytes(4).decode('utf-8')
        tick_packet = Tick(client, account_id, time_stamp, rand_bytes, enc_name)
        tick_packet.set_packet_buffer(reader)
        # reply to tick Message
        await client.send(tick_packet)
        return tick_packet

    def finalize(self):
        writer = Writer(self.PACKET_SIZE, is_game_server_packet=True)
        writer.write_int_in_bytes(self.PACKET_SIZE, 2)
        writer.write_int_in_bytes(self.PACKET_ID, 2)
        writer.write_int_in_bytes(self.account_id, 4)
        writer.write_byte_array(bytes.fromhex("6136AD26"))
        writer.write_byte_array(bytes.fromhex("D550282DE200310A2511AD442774E375"))
        writer.write_byte_array(bytes.fromhex("66D40000"))

        writer.write_string_in_bytes(Packet.packet_signature())
        self.data = writer.get_data()


    def __str__(self):
        self.print_row_packet()
        return f"[Tick Packet] Account Id {self.account_id} with Time Stamp {self.time_stamp} with Enc Name {self.enc_name}"