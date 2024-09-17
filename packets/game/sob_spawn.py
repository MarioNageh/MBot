from client.client import Client, ClientType
from data.sob_npc import SobNpc
from packets.packet import Packet
from processors.async_processor import Handlers
from utils.reader import Reader
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.game_client import GameClient


class SpawnSobMsg(Packet):
    PACKET_ID = 1109
    PACKET_SIZE = 0xDEADBEEF
    CLIENT_TYPE = ClientType.Game

    def __init__(self, client: Client
                 , sob_uuid: int
                 , max_health: int
                 , health: int
                 , x: int
                 , y: int
                 , mesh: int
                 , flag: int
                 , sob_type: int
                 ):
        super().__init__(client)
        self.sob_uuid = sob_uuid
        self.max_health = max_health
        self.health = health
        self.x = x
        self.y = y
        self.mesh = mesh
        self.flag = flag
        self.sob_type = sob_type

    @staticmethod
    def packet_action(data):
        packet: SpawnSobMsg = data
        client: 'GameClient' = packet.client
        sob_npc: SobNpc = SobNpc(packet.sob_uuid, packet.max_health, packet.health,
                                 packet.x, packet.y,
                                 packet.mesh, packet.flag, packet.sob_type)


        client.player.sobNpcController.add_sob_npc(sob_npc)


    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):
        sob_uuid = reader.read_int_32()
        max_health = reader.read_int_32()
        health = reader.read_int_32()
        x = reader.read_int_16()
        y = reader.read_int_16()
        mesh = reader.read_int_16()
        flag = reader.read_int_16()
        sob_type = reader.read_int_16()
        spawn_sob_msg = SpawnSobMsg(client, sob_uuid, max_health, health, x, y, mesh, flag, sob_type)
        spawn_sob_msg.set_packet_buffer(reader)

        SpawnSobMsg.packet_action(spawn_sob_msg)
        return spawn_sob_msg

    def __str__(self):
        self.print_row_packet()
        return f"[SpawnSobMsg] sob_uuid: {self.sob_uuid}, max_health: {self.max_health}, health: {self.health}, x: {self.x}, y: {self.y}, mesh: {self.mesh}, flag: {self.flag}, sob_type: {self.sob_type}"

    def finalize(self):
        pass
