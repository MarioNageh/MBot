import enum
from client.client import Client, ClientType
from data.item import Item
from packets.packet import Packet
from processors.async_processor import Handlers
from utils.reader import Reader

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from client.game_client import GameClient


class ItemInfoAction(enum.Enum):
    '''
    short int
    '''
    AddItem = 1
    TradeItem = 2
    UpdateItem = 3
    ObserveOtherItem = 4
    AuctionItem = 5


class ItemLocation(enum.Enum):
    '''
    byte
    '''
    Inventory = 0
    Helmet = 1
    Necklace = 2
    Armor = 3
    RightHand = 4
    LeftHand = 5
    Ring = 6
    Talisman = 7
    Boots = 8
    Garment = 9
    Warehouse = 10
    Unknown = 11


class MsgItemInfo(Packet):
    PACKET_ID = 1008
    PACKET_SIZE = 48
    CLIENT_TYPE = ClientType.Game

    def __init__(self, client: Client
                 , item_unique_id: int
                 , item_id: int
                 , durability: int  # short int
                 , max_durability: int  # short int
                 , action: ItemInfoAction
                 , identify: int  # byte
                 , location: ItemLocation
                 , unknown1: int  # byte
                 , gem1: int  # byte
                 , gem2: int  # byte
                 , magic1: int  # byte
                 , magic2: int  # byte
                 , plus: int  # byte
                 , bless: int  # byte
                 , enchant: int  # byte
                 , locked: int  # byte
                 , color: int  # byte
                 ):
        super().__init__(client)
        self.item_unique_id = item_unique_id
        self.item_id = item_id
        self.durability = durability
        self.max_durability = max_durability
        self.action = ItemInfoAction(action) if action else None
        self.identify = identify
        self.location = ItemLocation(location)
        self.unknown1 = unknown1
        self.gem1 = gem1
        self.gem2 = gem2
        self.magic1 = magic1
        self.magic2 = magic2
        self.plus = plus
        self.bless = bless
        self.enchant = enchant
        self.locked = locked
        self.color = color

    @staticmethod
    def packet_action(data):
        packet: MsgItemInfo = data
        client: 'GameClient' = packet.client
        if packet.action == ItemInfoAction.AddItem:
            item: Item = Item(packet.item_unique_id, packet.item_id, packet.durability, packet.max_durability,
                              packet.identify, packet.location, packet.unknown1, packet.gem1, packet.gem2,
                              packet.magic1,
                              packet.magic2, packet.plus, packet.bless, packet.enchant, packet.locked, packet.color)
            client.player.item_holder.add_item(item)



        elif packet.action == ItemInfoAction.TradeItem:
            pass
        elif packet.action == ItemInfoAction.UpdateItem:
            pass
        elif packet.action == ItemInfoAction.ObserveOtherItem:
            pass
        elif packet.action == ItemInfoAction.AuctionItem:
            pass
        # print(f"Total Inventory Items: {client.player.item_holder.inventory_length}")

    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):

        item_unique_id = reader.read_int_32()
        item_id = reader.read_int_32()

        durability = reader.read_int_16()
        max_durability = reader.read_int_16()
        action = reader.read_int_16()
        location = reader.read_byte()
        identify = reader.read_byte()
        unknown1 = reader.read_int_32()
        gem1 = reader.read_byte()
        gem2 = reader.read_byte()
        magic1 = reader.read_byte()
        magic2 = reader.read_byte()
        plus = reader.read_byte()
        bless = reader.read_byte()
        enchant = reader.read_byte()
        locked = reader.read_byte()
        color = reader.read_byte()
        msg_item_info = MsgItemInfo(client, item_unique_id, item_id, durability, max_durability, action, identify,
                                    location, unknown1, gem1, gem2, magic1, magic2, plus, bless, enchant, locked, color)
        msg_item_info.set_packet_buffer(reader)

        MsgItemInfo.packet_action(msg_item_info)

        return msg_item_info

    def __str__(self):
        self.print_row_packet()
        return f"ItemInfo: item_unique_id={self.item_unique_id}, item_id={self.item_id}, durability={self.durability}, " \
               f"max_durability={self.max_durability}, action={self.action.name if self.action else None}, " \
               f"identify={self.identify}, location={self.location.name if self.location else None}, " \
               f"unknown1={self.unknown1}, gem1={self.gem1}, gem2={self.gem2}, magic1={self.magic1}, magic2={self.magic2}, " \
               f"plus={self.plus}, bless={self.bless}, enchant={self.enchant}, locked={self.locked}, color={self.color}"

    def finalize(self):
        pass
