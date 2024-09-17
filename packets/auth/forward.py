from abc import ABC

from client.client import Client, ClientType
from exceptions import AccountServerRefuseConnection, UsernameOrPasswordInvalid
from packets.packet import Packet
from processors.async_processor import AsyncProcessor, Handlers
from utils.reader import Reader


class Forward(Packet):
    PACKET_ID = 1055
    PACKET_SIZE = 0xDeadBeaf
    CLIENT_TYPE = ClientType.Auth

    def __init__(self, client: Client, account_id: int, status: int, ip: str, port: int):
        super().__init__(client)
        self.account_id = account_id
        self.status = status
        self.ip = ip
        self.port = port

    @staticmethod
    @Handlers.async_register_packet_handler(PACKET_ID, CLIENT_TYPE)
    async def packet_processor(reader: Reader, client):
        account_id = reader.read_int_32()
        status = reader.read_int_32()
        if status == 10:
            raise AccountServerRefuseConnection(client, "Auth Server Refuse Connection [GameServer Error]")
        if status == 1:
            raise UsernameOrPasswordInvalid(client, "Account Server Refuse Connection [Invalid Account ID or Password]"
                                            , False)
        ip = reader.read_bytes(16).decode('utf-8').rstrip('\0')
        port = reader.read_int_32()
        forward = Forward(client, account_id, status, ip, port)
        forward.set_packet_buffer(reader)
        client.forward_packet = forward
        return forward

    def finalize(self):
        pass
