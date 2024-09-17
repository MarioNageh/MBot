import enum
from datetime import datetime

from client.client import Client, ClientType
from packets.packet import Packet
from processors.async_processor import Handlers
from utils.reader import Reader
from utils.time import get_current_time_stamp

from typing import TYPE_CHECKING

from utils.writer import Writer

if TYPE_CHECKING:
    from client.game_client import GameClient


class ChatType(enum.Enum):  # 2 byte
    Talk = 2000
    Whisper = 2001
    Action = 2002
    Team = 2003
    Syndicate = 2004
    System = 2005
    Family = 2006
    Talk2 = 2007
    Yelp = 2008
    Friend = 2009
    Global = 2010
    GM = 2011
    Ghost = 2013
    Serve = 2014
    World = 2021
    Register = 2100
    Broadcast = 2500


class Talk(Packet):
    PACKET_ID = 1004
    PACKET_SIZE = 0xDEADBEEF
    CLIENT_TYPE = ClientType.Game

    def __init__(self, client: Client
                 , color: int
                 , chat_type: ChatType
                 , style: int  # 2 byte
                 , receiver_look_face: int
                 , sender_look_face: int
                 , sender_name: str
                 , receiver_name: str
                 , message: str
                 , time_stamp: int = 0
                 ):
        super().__init__(client)
        self.color = color
        self.chat_type = chat_type
        self.style = style
        self.time_stamp = get_current_time_stamp(1) if time_stamp == 0 else time_stamp
        self.receiver_look_face = receiver_look_face
        self.sender_look_face = sender_look_face
        self.sender_name = sender_name
        self.receiver_name = receiver_name
        self.message = message
        pass

    @staticmethod
    def packet_action(data):
        packet: Talk = data
        client: GameClient = packet.client
        if packet.message.__contains__("coords") or packet.message.__contains__("invalid walk"):
            client.main_app.printer.print_fail(f"Invalid Coordinates: {packet.message}")
            if client.player:
                client.player.invalid_coordinates = True

    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):

        hex_color = reader.read_bytes(4)
        chat_type = reader.read_int_16()
        style = reader.read_int_16()
        time_stamp = reader.read_int_32()
        receiver_look_face = reader.read_int_32()
        sender_look_face = reader.read_int_32()
        unknown = reader.read_int_8()
        sender_name = reader.read_string_size_in_n_bytes(1, 'latin-1')
        receiver_name = reader.read_string_size_in_n_bytes(1, 'latin-1')
        reader.read_int_8()
        message = reader.read_string_size_in_n_bytes(1, 'latin-1')
        talk_packet = Talk(client, hex_color, chat_type, style, receiver_look_face, sender_look_face,
                           sender_name, receiver_name, message, time_stamp)

        talk_packet.set_packet_buffer(reader)
        Talk.packet_action(talk_packet)
        return talk_packet




    @staticmethod
    def talk_packet(client: Client, message: str, chat_type: ChatType = ChatType.Talk):
        talk_packet = Talk(client, 0, chat_type, 4, 0, 0, client.player.name, "", message)
        return talk_packet

    def finalize(self):
        # start with 2k buffer
        total_message_size = 26 + len(self.sender_name) + 6 + 1 + len(self.message)
        writer = Writer(total_message_size, is_game_server_packet=True)
        writer.write_int_in_bytes(total_message_size, 2) # 2 byte
        writer.write_int_in_bytes(self.PACKET_ID, 2) # 4 byte
        writer.write_byte_array(bytes.fromhex("ffffff00"))  # 8 byte
        writer.write_int_in_bytes(self.chat_type.value, 4)  # 12 byte
        current_time = datetime.now()
        sync_time = current_time.hour * 100 + current_time.minute
        writer.write_int_in_bytes(sync_time, 4)  # 16 byte
        writer.move_to_offset(24)  # total bytes 24
        writer.write_int_in_bytes(self.style, 1)  # total bytes 25
        writer.write_int_in_bytes(len(self.sender_name), 1)  # total bytes 26
        writer.write_string_in_bytes(self.sender_name, len(self.sender_name))  # total bytes 26 + len(sender_name)
        writer.write_byte_array(bytes.fromhex("04416C6C2000"))  # total bytes 26 + len(sender_name) + 6
        writer.write_int_in_bytes(len(self.message), 1)  # total bytes 26 + len(sender_name) + 6 + 1
        writer.write_string_in_bytes(self.message,
                                     len(self.message))  # total bytes 26 + len(sender_name) + 6 + 1 + len(message)
        writer.write_string_in_bytes(Packet.packet_signature())
        self.data = writer.get_data()

    def __str__(self):
        self.print_row_packet()
        return f"[Talk Packet] Sender: {self.sender_name} Receiver: {self.receiver_name} Message: {self.message}"
