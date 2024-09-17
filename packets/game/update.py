import enum

from client.client import Client, ClientType
from packets.packet import Packet
from processors.async_processor import Handlers
from utils.reader import Reader


class UpdateType(enum.Enum):
    """
    4 bytes
    """
    None_Type = 0xFFFFFFFF
    Life = 0
    MaxLife = 1
    Mana = 2
    MaxMana = 3
    Money = 4
    Experience = 5
    Pk = 6
    Profession = 7
    SizeAdd = 8
    Stamina = 9
    MoneySaved = 10
    AdditionalPoint = 11
    Look_face = 12
    Level = 13
    Spirit = 14
    Vitality = 15
    Strength = 16
    Agility = 17
    HeavenBlessing = 18
    DoubleExpTime = 19
    GuildDonation = 20
    CurseTime = 21
    AddTime = 22
    Reborn = 23
    UserStatus = 25
    StatusEffects = 26
    Hair = 27
    Xp = 28
    LuckyTime = 29
    CP = 30
    OnlineTraining = 32
    ExtraBP = 37
    Merchant = 39
    Quiz = 40
    EnlightPoints = 41
    BonusBP = 44
    BoundCp = 45
    AzureShield = 49
    Unknown = 36111349

    def __str__(self):
        return self.name


class UpdateData:
    def __init__(self, data: int = 0):
        self.data = data

    @property
    def data_low(self) -> int:
        return self.data & 0xFFFFFFFF

    @data_low.setter
    def data_low(self, value: int):
        self.data = (self.data & 0xFFFFFFFF00000000) | (value & 0xFFFFFFFF)

    @property
    def data_high(self) -> int:
        return (self.data >> 32) & 0xFFFFFFFF

    @data_high.setter
    def data_high(self, value: int):
        self.data = self.data_high | ((value & 0xFFFFFFFF) << 32)

    @property
    def signed_data(self) -> int:
        # 0x7FFFFFFFFFFFFFFF is the maximum signed 64-bit integer ((2**64)//2) - 1)
        # 0x10000000000000000 is the maximum unsigned 64
        return self.data if self.data <= 0x7FFFFFFFFFFFFFFF else self.data - 0x10000000000000000

    def __str__(self):
        return f"Data: {hex(self.data)} Data Low: {hex(self.data_low)} Data High: {hex(self.data_high)} Signed Data: {hex(self.signed_data)}"

    @signed_data.setter
    def signed_data(self, value: int):
        self.data = value & 0xFFFFFFFFFFFFFFFF


class UpdateMsg(Packet):
    PACKET_ID = 1017
    PACKET_SIZE = 0xDEADBEEF
    CLIENT_TYPE = ClientType.Game

    def __init__(self, client: Client
                 , player_uuid: int
                 , update_count: int
                 , update_type: UpdateType
                 , update_data: UpdateData
                 , update_data_2: UpdateData
                 ):
        super().__init__(client)
        self.player_uuid = player_uuid
        self.update_count = update_count
        self.update_type = update_type
        self.update_data = update_data
        self.update_data_2 = update_data_2

    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):
        player_uuid = reader.read_int_32()
        update_count = reader.read_int_32()
        update_type = UpdateType(reader.read_int_32())
        update_data = UpdateData(reader.read_int_64())
        update_data_2 = UpdateData(reader.read_int_64())
        update_msg_packet = UpdateMsg(client, player_uuid, update_count, update_type, update_data, update_data_2)
        update_msg_packet.set_packet_buffer(reader)
        return update_msg_packet

    def __str__(self):
        self.print_row_packet()
        return f"[Update Packet] Player UUID: {self.player_uuid} Update Count: {self.update_count} Update Type: {self.update_type} Update Data: {self.update_data} Update Data 2: {self.update_data_2}"

    def finalize(self):
        pass
