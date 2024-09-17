from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from cryptography.cryptography import Cryptography
from exceptions import ReceiveInCompletePacket, AccountServerRefuseConnection
from processors.async_processor import AsyncProcessor, Handlers, ProcessorTask, ProcessorTaskType
from sockets.as_game_socket import Socket
from utils.helpers import memcpy, to_hex_string
from utils.reader import Reader


class ClientType(Enum):
    Auth = 1
    Game = 2
    Enc = 3


class Client(ABC):

    def __init__(self, socket: Socket, main_app):
        from async_main import Mbot
        self.key_exchange = False
        self.main_app: Mbot = main_app
        self.socket: Socket = socket
        self.server_crypto: Optional[Cryptography] = None
        self.client_crypto: Optional[Cryptography] = None
        self.processor = None
        self.client_type: Optional[ClientType] = None

    async def send(self, data, send_immediately=False):
        data_encrypted = None
        if isinstance(data, bytearray):
            data_encrypted = self.client_crypto.encrypt(data)
        else:
            data_encrypted = self._send_packet(data)

        if send_immediately and self.socket.get_socket_state():
            await self.socket.send(data_encrypted)
            return

        task = ProcessorTask(ProcessorTaskType.Send, data_encrypted, self)
        self.main_app.processor.enqueue(task)

    # @abstractmethod
    def _send_packet(self, packet):
        packet.finalize()
        reader = Reader(packet.data)
        packet_size = reader.read_int_16()
        packet_id = reader.read_int_16()
        # print(f"Packet Size: {packet_size} Packet ID: {packet_id} To Be Sent")

        data_encrypted = self.client_crypto.encrypt(bytearray(packet.data))
        # if self.socket.get_socket_state():
        #     self.socket.get_socket().send(data_encrypted)
        return data_encrypted

    def disconnect(self):
        self.socket.close_socket()

    def handle_receive_multiple_packets(self, data: bytes):
        last_read_position = 0
        if self.check_if_multiple_packets(data):
            whole_packet_reader = Reader(data)
            whole_packet_size = len(data)

            while whole_packet_reader.position < whole_packet_size:
                packet_size = whole_packet_reader.read_int_16()
                total_packet_size = packet_size + 8
                packet_data = bytearray(total_packet_size)
                last_read_position = whole_packet_reader.position - 2
                if whole_packet_reader.position + total_packet_size > whole_packet_size:
                    raise ReceiveInCompletePacket(self,
                                                  f'Index Error, Last Read Position: {last_read_position}',
                                                  last_read_position, data)

                memcpy(packet_data, data, total_packet_size, whole_packet_reader.position - 2)
                whole_packet_reader.move_cursor_to(whole_packet_reader.position - 2 + total_packet_size)
                yield Reader(packet_data)

        else:
            yield Reader(data)

    def check_if_multiple_packets(self, data: bytes):
        reader = Reader(data)
        packet_size = reader.read_int_16()
        packet_id = reader.read_int_16()
        total_packet_length = len(data)
        if self.key_exchange and (packet_size + 8) != total_packet_length:
            # this check for first corrupted packet due to iv error will handle it later
            reader.read_int_32()
            next_ushort = reader.read_int_16()

            if next_ushort == 2101:  # the error packet
                return False
            # print(f"Packet Size: {packet_size} Total Packet Length: {total_packet_length}")
            return True
        return False

    def decrypt_server_packet(self, data):
        self.server_crypto.decrypt(data)

    async def packet_handler(self, data, needs_to_decrypt=True):
        try:
            if needs_to_decrypt:
                self.decrypt_server_packet(data)
            for reader in self.handle_receive_multiple_packets(data):
                packet_size = reader.read_int_16()
                packet_id = reader.read_int_16()
                packet_handler = Handlers.get_packet_handler(packet_id, self.client_type)
                packet_received = reader
                if packet_handler:

                    packet_received = await self.main_app.add_awaitable_to_event_loop(packet_handler(reader, self))
                    # packet_received = await packet_handler(reader, self)
                else:
                    pass
                    # print(f"Packet Not Found {packet_id}")
                yield packet_received

        except ReceiveInCompletePacket as e:
            incomplete_part = data[e.last_read_position:]
            '''
            We Will Add The Packet To The Queue Again To Be Processed When The Packet Is Complete
            '''
            task: ProcessorTask = ProcessorTask(ProcessorTaskType.ReceiveIncomplete, incomplete_part, self)
            self.main_app.processor.enqueue(task)

        except Exception as e:
            self.main_app.printer.print_fail(f"Packet Have An Error,{e}")
            await self.error_handler(e)

    @abstractmethod
    def on_finish_process(self, packet):
        print(packet)

    def error_handler(self, exception: Exception):
        pass


    async def start_client(self):
        await self.socket.start_receive()