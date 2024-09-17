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


class WalkMode(enum.Enum):
    Walk = 0
    Run = 1

    def __int__(self):
        return self.name


class Walk(Packet):
    PACKET_ID = 1005
    PACKET_SIZE = 16
    CLIENT_TYPE = ClientType.Game

    def __init__(self, client
                 , user_id: int
                 , direction: int
                 , mode: int
                 , time_stamp: int = 0):
        super().__init__(client)
        self.user_id = user_id
        self.direction = direction
        self.mode = WalkMode(mode)
        self.time_stamp = time_stamp if time_stamp else get_current_time_stamp(self.user_id)

    @staticmethod
    def packet_action(data):
        packet: Walk = data
        client: 'GameClient' = packet.client
        player: Player = client.player
        # check if current user that move to update location
        if packet.user_id == client.player.user_id:
            client.player.update_position(packet.direction)
            if player.player_finding_his_way:
                pass
                client.main_app.kernel.add_event(Event.create_event_from_callback(client, move_to_sob_npc))


    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):

        user_id = reader.read_int_32()
        direction = reader.read_int_8()
        mode = reader.read_int_8()
        reader.read_int_16()

        time_stamp = reader.read_int_32()
        walk_packet = Walk(client, user_id, direction, mode, time_stamp)
        walk_packet.set_packet_buffer(reader)
        Walk.packet_action(walk_packet)

        return walk_packet

    def finalize(self):
        writer = Writer(self.PACKET_SIZE, is_game_server_packet=True)
        writer.write_int_in_bytes(self.PACKET_SIZE, 2)
        writer.write_int_in_bytes(self.PACKET_ID, 2)
        writer.write_int_in_bytes(self.user_id, 4)
        writer.write_int_in_bytes(self.direction % 8, 1)
        writer.write_int_in_bytes(self.mode.value, 1)
        writer.write_int_in_bytes(0, 2)
        writer.write_int_in_bytes(self.time_stamp, 4)
        writer.write_string_in_bytes(Packet.packet_signature())
        self.data = writer.get_data()

    def __str__(self):
        self.print_row_packet()
        return f"[Walk Packet] User ID {self.user_id} with Direction {self.direction} with Mode {self.mode} with Time Stamp {self.time_stamp}"
