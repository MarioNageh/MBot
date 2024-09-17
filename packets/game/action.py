import enum
from client.client import Client, ClientType
from constants import Maps, ConstantShops, ConstantItems, Coordinate
from packets.packet import Packet
from processors.events import move_to_sob_npc
from processors.async_processor import AsyncProcessor, Handlers

from utils.reader import Reader
from utils.time import get_current_time_stamp
from typing import TYPE_CHECKING, Optional

from utils.writer import Writer

if TYPE_CHECKING:
    from client.game_client import GameClient


class ActionType(enum.Enum):
    """
    4 bytes
    """
    SetLocation = 74
    Hotkeys = 75
    ConfirmFriends = 76
    ConfirmProficiencies = 77
    ConfirmSkills = 78
    ChangeDirection = 79
    ChangeAction = 81
    UsePortal = 85
    Teleport = 86
    Leveled = 92
    RemoveXp = 93
    Revive = 94
    Delete = 95
    ChangePKMode = 96
    ConfirmGuild = 97
    Mine = 99
    InvisibleEntity = 102
    ScreenColor = 104
    TeamateLoc = 106
    NewCoordinates = 108
    DropMagic = 109
    DropSkill = 110
    Vend = 111
    GetSurroundings = 114
    OpenCustom = 116
    ObserveEquipment = 117
    CancelDisguise = 118
    CancelFly = 120
    GoldPickup = 121
    EnemyInfo = 123
    OpenWindow = 126
    CompleteLogin = 130
    SpawnEffect = 131
    RemoveEntity = 132
    Jump = 133
    SetGhost = 137
    FriendInfo = 140
    ChangeFace = 142
    EndTeleport = 146
    ItemsDetained = 154
    DetainItems = 155
    Shift = 156
    HideInterface = 158
    BlueCountdown = 159
    OpenUpgrade = 160
    PathFind = 162
    AbortMagic = 163
    MapARGB = 164
    MobDropsDragonball = 165
    ObserveFriend = 310
    Unknown = 128
    Unknown1 = 100
    Unknown2 = 138

    def __str__(self):
        return self.name


class ActionData:
    def __init__(self, data: int = 0):
        self.data = data & 0xFFFFFFFF  # Ensure data is within 32-bit bounds

    @property
    def data_low(self) -> int:
        # Extract the lower 16 bits of the 32-bit data
        return self.data & 0xFFFF

    @data_low.setter
    def data_low(self, value: int):
        # Set the lower 16 bits, preserving the upper 16 bits
        self.data = (self.data & 0xFFFF0000) | (value & 0xFFFF)

    @property
    def data_high(self) -> int:
        # Extract the upper 16 bits of the 32-bit data
        return (self.data >> 16) & 0xFFFF

    @data_high.setter
    def data_high(self, value: int):
        # Set the upper 16 bits, preserving the lower 16 bits
        self.data = (self.data_low) | ((value & 0xFFFF) << 16)

    @property
    def signed_data(self) -> int:
        # Handle signed 32-bit integer
        return self.data if self.data <= 0x7FFFFFFF else self.data - 0x100000000

    @signed_data.setter
    def signed_data(self, value: int):
        self.data = value & 0xFFFFFFFF  # Ensure the value is within 32-bit bounds

    def __str__(self):
        return f"Data: {hex(self.data)} Data Low: {hex(self.data_low)} Data High: {hex(self.data_high)} Signed Data: {hex(self.signed_data)}"


class ActionMsg(Packet):
    PACKET_ID = 1010
    PACKET_SIZE = 28
    CLIENT_TYPE = ClientType.Game

    def __init__(self, client: Client
                 , user_id: int
                 , data_one: ActionData
                 , data_two: ActionData
                 , data_three: int
                 , action: ActionType
                 , time_stamp: int = 0
                 ):
        super().__init__(client)
        self.user_id = user_id
        self.time_stamp = time_stamp if time_stamp != 0 else get_current_time_stamp(self.user_id)
        self.data_one = data_one
        self.data_two = data_two
        self.data_three = data_three
        self.action = action

    @staticmethod
    async def packet_action(data):
        packet: ActionMsg = data
        client: 'GameClient' = packet.client
        if packet.action in [
                             ActionType.Jump
                             ] and packet.user_id != client.player.user_id:
            return
        if packet.action == ActionType.SetLocation or packet.action == ActionType.Teleport:
            map_id = packet.data_one.data_low
            x = packet.data_two.data_low
            y = packet.data_two.data_high
            client.player.set_position(map_id, x, y)
            if client.player.map_id != Maps.TwinCity:
                await client.player.item_holder.buy_item(ConstantShops.ShoppingMall, ConstantItems.TwinCityGate, 1)
                client.main_app.printer.print_info(f"Has Bought TwinCityGate")
            else:
                await client.player.item_holder.buy_item(ConstantShops.ShoppingMall, ConstantItems.TwinCityGate, 1)
                client.main_app.printer.print_info(f"Has Bought TwinCityGate")
        if packet.action == ActionType.Jump:
            x = packet.data_one.data_low
            y = packet.data_one.data_high
            client.player.set_position(client.player.map_id, x, y)
            if client.player.player_finding_his_way:
                pass
                from processors.kernel import Event
                client.main_app.kernel.add_event(Event.create_event_from_callback(client, move_to_sob_npc))

    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):
        time_stamp = reader.read_int_32()  # offset 4
        user_id = reader.read_int_32()  # offset 8
        data_one = ActionData(reader.read_int_32())  # offset 12
        data_two = ActionData(reader.read_int_32())  # offset 16
        data_three = reader.read_int_16()  # offset 20
        action = ActionType(reader.read_int_16())  # offset 22
        action_packet = ActionMsg(client, user_id, data_one, data_two, data_three, action, time_stamp)
        action_packet.set_packet_buffer(reader)
        await ActionMsg.packet_action(action_packet)

        return action_packet

    def finalize(self):
        writer = Writer(self.PACKET_SIZE, is_game_server_packet=True)
        writer.write_int_in_bytes(self.PACKET_SIZE, 2)
        writer.write_int_in_bytes(self.PACKET_ID, 2)
        writer.write_int_in_bytes(self.time_stamp, 4)
        writer.write_int_in_bytes(self.user_id, 4)
        writer.write_int_in_bytes(self.data_one.data, 4)
        writer.write_int_in_bytes(self.data_two.data, 4)
        writer.write_int_in_bytes(self.data_three, 2)
        writer.write_int_in_bytes(self.action.value, 2)
        writer.write_int_in_bytes(0, 4)
        writer.write_string_in_bytes(Packet.packet_signature())
        self.data = writer.get_data()

    @staticmethod
    def jump_packet(client: Client, user_id: int
                    , to_cord: Coordinate
                    , from_cord: Optional[Coordinate] = None):

        if from_cord is None and client.player:
            from_cord = client.player.position

        from_data: ActionData = ActionData(0)
        from_data.data_low = from_cord.x
        from_data.data_high = from_cord.y

        to_data: ActionData = ActionData(0)
        to_data.data_low = to_cord.x
        to_data.data_high = to_cord.y

        packet = ActionMsg(client
                           , user_id
                           , to_data
                           , from_data
                           , 0
                           , ActionType.Jump)

        return packet

    def __str__(self):
        self.print_row_packet()
        return f"[Action Type] User Id: {self.user_id} Time Stamp: {self.time_stamp} Data One: {self.data_one} Data Two: {self.data_two} Data Three: {self.data_three} Action: {self.action}"
