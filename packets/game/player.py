from client.client import Client, ClientType
from exceptions import UserNotHaveEnoughCps, InventoryFull
from packets.packet import Packet
from processors.kernel import Event
from processors.async_processor import Handlers
from utils.reader import Reader
from data.player import Player as HeroInfo
from packets.game.action import ActionMsg, ActionType, ActionData

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.game_client import GameClient


class Player(Packet):
    PACKET_ID = 1006
    PACKET_SIZE = 0xDEADBEEF
    CLIENT_TYPE = ClientType.Game

    def __init__(self, client: Client
                 , user_id: int
                 , look_interface: int
                 , hair: int
                 , money: int
                 , cps: int
                 , name: str
                 , profession: int = None
                 ):
        super().__init__(client)
        self.user_id = user_id
        self.look_interface = look_interface
        self.hair = hair
        self.money = money
        self.cps = cps
        self.name = name
        self.profession = profession

    @staticmethod
    async def packet_action(data):
        packet: Player = data
        client: 'GameClient' = packet.client

        # update player data
        client.player = HeroInfo(client
                                 , packet.user_id
                                 , packet.look_interface
                                 , packet.hair
                                 , packet.money
                                 , packet.cps
                                 , packet.name
                                 , profession=packet.profession
                                 )

        client.main_app.printer.print_success(
            f"Has Login Successfully with {packet.cps} Cps account: {client.main_app.user_name}, password: {client.main_app.password}")

        if client.player.user_cps < 100:
            raise UserNotHaveEnoughCps(client, f"{packet.name} Player Cps is less than 100")


        # Request Player Location
        action_packet = ActionMsg(client, packet.user_id,
                                  ActionData(0), ActionData(0),
                                  0, ActionType.SetLocation)
        await client.send(action_packet)

        # For Requesting Player Items
        hotkeys_packet = ActionMsg(client, packet.user_id,
                                   ActionData(0), ActionData(0),
                                   0, ActionType.Hotkeys)
        await client.send(hotkeys_packet)

        # Change To PKMode
        action_packet = ActionMsg(client, packet.user_id,
                                  ActionData(1), ActionData(0),
                                  0, ActionType.ChangePKMode)
        await client.send(action_packet)

        from processors.events import check_player_inventory
        client.main_app.kernel.add_event(Event.create_event_from_callback(client, check_player_inventory))

    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):
        user_id = reader.read_int_32()
        look_interface = reader.read_int_32()
        hair = reader.read_int_16()
        money = reader.read_int_32()
        cps = reader.read_int_32()
        experience = reader.read_int_64()
        strength = reader.read_int_16()
        agility = reader.read_int_16()
        vitality = reader.read_int_16()
        spirit = reader.read_int_16()
        stats = reader.read_int_16()
        life = reader.read_int_16()
        mana = reader.read_int_16()
        pk_points = reader.read_int_16()
        reader.move_cursor_to(66)
        level = reader.read_int_8()

        class_id = reader.read_int_8()
        reborn = reader.read_int_8()

        reader.move_cursor_to(72)
        name_size = reader.read_int_8()
        name = reader.read_bytes(name_size).decode('latin-1')
        player_packet = Player(client, user_id, look_interface, hair, money, cps, name
                               , profession=class_id
                               )
        player_packet.set_packet_buffer(reader)

        await Player.packet_action(player_packet)

        return player_packet

    def __str__(self):
        self.print_row_packet()
        return f"[Player Packet] Username {self.name} with Cps {self.cps} With Id {self.user_id}"

    def finalize(self):
        pass
