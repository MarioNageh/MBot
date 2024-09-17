import enum

from client.client import Client, ClientType
from packets.packet import Packet
from processors.async_processor import Handlers
from utils.reader import Reader
from utils.writer import Writer
from utils.time import get_current_time_stamp


class ItemAction(enum.Enum):
    BuyFromNPC = 1
    SellToNPC = 2
    RemoveInventory = 3
    DropItem = 3
    EquipItem = 4
    SetEquipItem = 5
    UnEquipItem = 6
    SplitItem = 7
    ViewWarehouse = 9
    WarehouseDeposit = 10
    WarehouseWithdraw = 11
    DropMoney = 12
    RepairItem = 14
    DragonBallUpgrade = 19
    MeteorUpgrade = 20
    BoothQuery = 21
    BoothAdd = 22
    BoothDelete = 23
    BoothBuy = 24
    Ping = 27
    Enchant = 28
    BoothAddCP = 29

    def __str__(self):
        return self.name


class MsgItem(Packet):
    PACKET_ID = 1009
    PACKET_SIZE = 28
    CLIENT_TYPE = ClientType.Game

    def __init__(self, client: Client, uid: int, id: int, action: ItemAction, amount: int, time_stamp: int = 0):
        super().__init__(client)
        self.uid = uid
        self.id = id
        self.action = action
        self.time_stamp = time_stamp if time_stamp else get_current_time_stamp(1)
        self.amount = amount

    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):
        uid = reader.read_int_32()
        id = reader.read_int_32()
        action = reader.read_int_32()
        time_stamp = reader.read_int_32()
        amount = reader.read_int_32()
        msg_item = MsgItem(client, uid, id, action, time_stamp, amount)
        msg_item.set_packet_buffer(reader)
        return msg_item

    def finalize(self):
        writer = Writer(self.PACKET_SIZE, is_game_server_packet=True)
        writer.write_int_in_bytes(self.PACKET_SIZE, 2)
        writer.write_int_in_bytes(self.PACKET_ID, 2)
        writer.write_int_in_bytes(self.uid, 4)
        writer.write_int_in_bytes(self.id, 4)
        writer.write_int_in_bytes(self.action.value, 4)
        writer.write_int_in_bytes(self.time_stamp, 4)
        writer.write_int_in_bytes(self.amount, 4)
        writer.write_int_in_bytes(0, 4)
        writer.write_string_in_bytes(Packet.packet_signature())
        self.data = writer.get_data()
        pass

    def __str__(self):
        self.print_row_packet()
        return f"[MsgItem Packet] UID {self.uid} with ID {self.id} with Action {self.action} with Time Stamp {self.time_stamp} with Amount {self.amount}"
