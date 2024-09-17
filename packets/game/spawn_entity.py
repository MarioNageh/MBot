import enum

from client.client import Client, ClientType
from packets.packet import Packet
from processors.async_processor import Handlers
from utils.reader import Reader


class ClientEffect(enum.Enum):
    """
     4-byte
    """
    None_Effect = 0x00000000
    Blue = 1 << 0
    Poison = 1 << 1
    NoBody = 1 << 2
    Die = 1 << 3
    XpStart = 1 << 4
    Dead = 1 << 5
    TeamLeader = 1 << 6
    Accuracy = 1 << 7
    Shield = 1 << 8
    Stigma = 1 << 9
    Ghost = 1 << 10
    Fade = 1 << 11
    Unknown12 = 1 << 12
    Unknown13 = 1 << 13
    Red = 1 << 14
    Black = 1 << 15
    Unknown16 = 1 << 16
    Reflect = 1 << 17
    Superman = 1 << 18
    Unknown19 = 1 << 19
    Unknown20 = 1 << 20
    Unknown21 = 1 << 21
    Invisible = 1 << 22
    Cyclone = 1 << 23
    Unknown24 = 1 << 24
    Unknown25 = 1 << 25
    Dodge = 1 << 26
    Fly = 1 << 27
    Intensify = 1 << 28
    Unknown29 = 1 << 29
    LuckDiffuse = 1 << 30
    LuckAbsorb = 1 << 31
    All = 0xFFFFFFFF
    Unkonwn30 = 8388624
    Unkonwn31 = 1073742336
    Unkonwn32 = 1056
    Unkonwn33 = 33280
    Unkonwn34 = 16400

    def __str__(self):
        return self.name


class ActionType(enum.Enum):
    Dance = 1
    None_Action = 100
    Laugh = 150
    Guffaw = 151
    Angry = 160
    Sad = 170
    Excited = 180
    Wave = 190
    Salute = 200
    Think = 210
    Kneel = 220
    Cool = 230
    Swim = 240
    Sit = 250
    Lie = 270
    Unknown = 128
    Unknown1 = 0
    Unknown2 = 80
    def __str__(self):
        return self.name

class SpawnEntityMsg(Packet):
    PACKET_ID = 1014
    PACKET_SIZE = 0xDEADBEEF
    CLIENT_TYPE = ClientType.Game

    def __init__(self, client: Client
                 , entity_uuid: int
                 , entity_look_face: int
                 , entity_status: ClientEffect
                 , guild_id: int
                 , guild_rank: int
                 , garment_type: int
                 , helmet_type: int
                 , armor_type: int
                 , weapon_l_type: int
                 , weapon_r_type: int
                 , unknown2: int
                 , life: int
                 , level: int
                 , position_x: int
                 , position_y: int
                 , hair: int
                 , direction: int
                 , action: ActionType
                 , reborn_count: int
                 , unknown4: int
                 , unknown5: int
                 , nobility: int
                 , nobility_rank: int
                 , unknown6: int
                 , helmet_color: int
                 , armor_color: int
                 , entity_name: str
                 , entity_supposed_name: str
                 ):
        super().__init__(client)
        self.entity_uuid = entity_uuid
        self.entity_look_face = entity_look_face
        self.entity_status = entity_status
        self.guild_id = guild_id
        self.guild_rank = guild_rank
        self.garment_type = garment_type
        self.helmet_type = helmet_type
        self.armor_type = armor_type
        self.weapon_l_type = weapon_l_type
        self.weapon_r_type = weapon_r_type
        self.unknown2 = unknown2
        self.life = life
        self.level = level
        self.position_x = position_x
        self.position_y = position_y
        self.hair = hair
        self.direction = direction
        self.action = action
        self.reborn_count = reborn_count
        self.unknown4 = unknown4
        self.unknown5 = unknown5
        self.nobility = nobility
        self.nobility_rank = nobility_rank
        self.unknown6 = unknown6
        self.helmet_color = helmet_color
        self.armor_color = armor_color
        self.entity_name = entity_name
        self.entity_supposed_name = entity_supposed_name


    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):

        entity_uuid = reader.read_int_32()
        entity_look_face = reader.read_int_32()

        en_status = reader.read_int_32()
        try:
            entity_status = ClientEffect(en_status)
        except ValueError:
            client.main_app.printer.print_fail(f"Unknown Entity Status: {en_status}")
            entity_status = ClientEffect.None_Effect
        guild_id = reader.read_int_32()
        guild_rank = reader.read_int_32()
        garment_type = reader.read_int_32()
        helmet_type = reader.read_int_32()
        armor_type = reader.read_int_32()
        weapon_l_type = reader.read_int_32()
        weapon_r_type = reader.read_int_32()
        unknown2 = reader.read_int_32()
        life = reader.read_int_16()
        level = reader.read_int_16()
        position_x = reader.read_int_16()
        position_y = reader.read_int_16()
        hair = reader.read_int_16()
        direction = reader.read_int_8()
        action = ActionType(reader.read_int_8())
        reborn_count = reader.read_int_8()

        level2 = reader.read_int_16()
        helmet_color = reader.read_int_8()
        armor_color = reader.read_int_8()
        nobility = reader.read_int_8()
        nobility_rank = reader.read_int_32()
        unknown6 = 0

        unknown5 = 0
        reader.move_cursor_to(91)


        number_of_strings = reader.read_int_8()
        entity_name = reader.read_string_size_in_n_bytes(1,'latin-1')
        entity_supposed_name = ""
        if number_of_strings > 1:
            entity_supposed_name = reader.read_string_size_in_n_bytes(1)
        spawn_entity_msg = SpawnEntityMsg(client
                                          , entity_uuid
                                          , entity_look_face
                                          , entity_status
                                          , guild_id
                                          , guild_rank
                                          , garment_type
                                          , helmet_type
                                          , armor_type
                                          , weapon_l_type
                                          , weapon_r_type
                                          , unknown2
                                          , life
                                          , level
                                          , position_x
                                          , position_y
                                          , hair
                                          , direction
                                          , action
                                          , reborn_count
                                          , level2
                                          , unknown5
                                          , nobility
                                          , nobility_rank
                                          , unknown6
                                          , helmet_color
                                          , armor_color
                                          , entity_name
                                          , entity_supposed_name
                                          )
        spawn_entity_msg.set_packet_buffer(reader)
        return spawn_entity_msg
        pass

    def finalize(self):
        pass

    def __str__(self):
        self.print_row_packet()
        return f"[SpawnEntityMsg] {self.entity_name} - {self.entity_supposed_name} - {self.entity_uuid} - {self.entity_status} - {self.action} - {self.direction} - {self.life} - {self.level} - {self.position_x} - {self.position_y} - {self.hair} - {self.reborn_count} - {self.nobility} - {self.nobility_rank} - {self.entity_supposed_name} - {self.entity_supposed_name}"