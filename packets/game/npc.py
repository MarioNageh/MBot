from client.client import Client, ClientType
from packets.packet import Packet
from processors.async_processor import Handlers
from utils.reader import Reader

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.game_client import GameClient


class NpcMsg(Packet):
    PACKET_ID = 2030
    PACKET_SIZE = 20
    CLIENT_TYPE = ClientType.Game

    def __init__(self, client: Client
                 , npc_id: int
                 , npc_x: int
                 , npc_y: int
                 , npc_look_face: int
                 , npc_type: int
                 , npc_role: int
                 ):
        super().__init__(client)
        self.npc_id = npc_id
        self.npc_x = npc_x
        self.npc_y = npc_y
        self.npc_look_face = npc_look_face
        self.npc_type = npc_type
        self.npc_role = npc_role

    @staticmethod
    def packet_action(data):
        packet: NpcMsg = data
        client: 'GameClient' = packet.client
        # TODO Add NPC

    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):
        npc_id = reader.read_int_32()
        npc_x = reader.read_int_16()
        npc_y = reader.read_int_16()
        npc_look_face = reader.read_int_16()
        npc_type = reader.read_int_16()
        npc_role = reader.read_int_16()

        npc_msg = NpcMsg(client, npc_id, npc_x, npc_y, npc_look_face, npc_type, npc_role)
        npc_msg.set_packet_buffer(reader)
        NpcMsg.packet_action(npc_msg)
        return npc_msg

    def __str__(self):
        self.print_row_packet()
        return f"[NPC MSG] {self.npc_id} {self.npc_x} {self.npc_y} {self.npc_look_face} {self.npc_type} {self.npc_role}"

    def finalize(self):
        pass
