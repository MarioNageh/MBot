import enum
from typing import TYPE_CHECKING

from client.client import Client, ClientType
from data.player import Player
from packets.packet import Packet
from processors.events import move_to_sob_npc
from processors.kernel import Event
from processors.async_processor import Handlers
from utils.reader import Reader
from utils.time import get_current_time_stamp
from utils.writer import Writer

if TYPE_CHECKING:
    from client.game_client import GameClient


class InteractAction(enum.Enum):
    Attack = 2
    Kill = 14
    Unknown = 25
    Unknown1 = 21
    def __int__(self):
        return self.name


class InteractMsg(Packet):
    PACKET_ID = 1022
    PACKET_SIZE = 33
    CLIENT_TYPE = ClientType.Game

    def __init__(self, client
                 , user_id: int
                 , target_id: int
                 , target_x: int
                 , target_y: int
                 , action: InteractAction
                 , value: int
                 , time_stamp: int = None):
        super().__init__(client)
        self.time_stamp = time_stamp if time_stamp else get_current_time_stamp(user_id)
        self.user_id = user_id
        self.target_id = target_id
        self.target_x = target_x
        self.target_y = target_y
        self.action = action
        self.value = value

    @staticmethod
    async def packet_action(data):
        packet: InteractMsg = data
        client: 'GameClient' = packet.client
        player: Player = client.player
        pass

    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client: Client):
        time_stamp = reader.read_int_32()
        user_id = reader.read_int_32()
        target_id = reader.read_int_32()
        target_x = reader.read_int_16()
        target_y = reader.read_int_16()
        action = InteractAction(reader.read_int_32())
        value = reader.read_int_n(9)
        interact_packet = InteractMsg(client, user_id, target_id, target_x, target_y, action, value, time_stamp)
        interact_packet.set_packet_buffer(reader)
        await InteractMsg.packet_action(interact_packet)
        return interact_packet

    def finalize(self):
        writer = Writer(self.PACKET_SIZE, is_game_server_packet=True)
        writer.write_int_in_bytes(self.PACKET_SIZE, 2)
        writer.write_int_in_bytes(self.PACKET_ID, 2)
        writer.write_int_in_bytes(self.time_stamp, 4)
        writer.write_int_in_bytes(self.user_id, 4)
        writer.write_int_in_bytes(self.target_id, 4)
        writer.write_int_in_bytes(self.target_x, 2)
        writer.write_int_in_bytes(self.target_y, 2)
        writer.write_int_in_bytes(self.action.value, 4)
        writer.write_int_in_bytes(self.value, 9)
        writer.write_string_in_bytes(Packet.packet_signature())
        self.data = writer.get_data()

    def __str__(self):
        self.print_row_packet()
        return f"[InteractMsg]: user_id: {self.user_id}, target_id: {self.target_id}, target_x: {self.target_x}, " \
               f"target_y: {self.target_y}, action: {self.action}, value: {self.value}, time_stamp: {self.time_stamp}"
