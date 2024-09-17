from utils.helpers import memcpy


class Reader:
    def __init__(self, buffer):
        self.buffer = memoryview(buffer)
        self._buffer = buffer
        self.position = 0

    def move_cursor_to(self, position):
        self.position = position

    def read_bytes(self, size):
        data = bytearray(size)
        memcpy(data, self._buffer, size, self.position)
        self.position += size
        return data

    def read_byte(self):
        return self.read_int_n(1)

    def read_int_16(self):
        return self.read_int_n(2)

    def read_int_8(self):
        return self.read_int_n(1)

    def read_int_32(self):
        return self.read_int_n(4)

    def read_int_64(self):
        return self.read_int_n(8)

    def read_string(self,encoding='utf-8'):
        size = self.read_int_16()
        data = bytearray(size)
        memcpy(data, self._buffer, size, self.position)
        self.position += size
        return data.decode(encoding)

    def read_string_size_in_n_bytes(self, n, encoding='utf-8'):
        size = self.read_int_n(n)
        data = bytearray(size)
        memcpy(data, self._buffer, size, self.position)
        self.position += size
        return data.decode(encoding)


    def read_int_n(self, size):
        number = 0
        for i in range(size):
            number = number | self.buffer[self.position] << (8 * i)
            self.position += 1
        return number

    def to_hex_string(self, is_space=False):
        return (''.join(' {:02x}'.format(x) for x in self.buffer))[1::] if not is_space else (
            ''.join(' {:02x}'.format(x) for x in self.buffer))

    def __str__(self):
        return self.to_hex_string()
