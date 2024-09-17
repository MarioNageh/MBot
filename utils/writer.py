class Writer:
    def __init__(self, packet_size: int = 1024 * 8, is_game_server_packet=False):
        self.is_game_server_packet = is_game_server_packet
        self.packet_size = packet_size
        if is_game_server_packet:
            self.packet_size = self.packet_size + 8
        self.position = 0
        self.packet_data = memoryview(bytearray(self.packet_size))

    def __str__(self) -> str:
        return self.to_hex_string()

    def print_to_last_position(self):
        return self.to_hex_string(self.packet_data[:self.position])

    def get_data(self) -> memoryview:
        return self.packet_data

    def move_to_offset(self, number: int) -> None:
        self.position = number

    def to_hex_string(self,data: memoryview = None) -> str:
        if data is not None:
            return (''.join(' {:02x}'.format(x) for x in data))[1::]
        return (''.join(' {:02x}'.format(x) for x in self.packet_data))[1::]

    def write_int_in_bytes(self, number: int, bytes_number: int = 2):
        bytes_array: bytes = number.to_bytes(bytes_number, 'little')
        self.write_byte_array(bytes_array)

    def write_byte_array(self, byte_array_of_data: bytes):
        for i in range(len(byte_array_of_data)):
            self.packet_data[self.position] = byte_array_of_data[i]
            self.position += 1

    def write_string_in_bytes(self, word: str, bytes_number: int = 16):
        if len(word) > bytes_number:
            raise Exception("The Word Must be Less Or Equal bytes Number")

        rest_of_sen = bytes_number - len(word.encode('utf-8'))
        bytes_array: bytes = word.encode()
        self.write_byte_array(bytes_array)
        self.position += rest_of_sen
