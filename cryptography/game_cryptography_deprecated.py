from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad
from crypto.cryptography import Cryptography
from utils.helpers import to_hex_string, memcpy


class GameCryptographyOld(Cryptography):
    def __init__(self, key, client, is_key_exchange=False, ini_vector=bytearray(8), is_padding=False):
        self.key = key
        self.iv_one = bytearray(8)
        self.iv_two = bytearray(8)
        self.iv = ini_vector
        self.client = client
        self.key_exchange = is_key_exchange
        self.is_padding = is_padding
        # if self.key_exchange:
        #     return
        self.key = self.blowfish_set_key(key)
        key = self.key
        if type(key) is bytes:
            # self.cipher = Cipher(algorithms.Blowfish(key), modes.CFB(bytearray(8)))
            # self.cipher = blowfish.Cipher(self.key)
            # self.cipher = Cipher(algorithms.Blowfish(key), modes.CFB(ini_vector))
            self.cipher = Blowfish.new(key, Blowfish.MODE_CFB, iv=ini_vector, segment_size=64)

        else:
            # self.cipher = Cipher(algorithms.Blowfish(key.encode('utf-8')), modes.CFB(ini_vector))
            self.cipher = Blowfish.new(key.encode('utf-8'), Blowfish.MODE_CFB, iv=ini_vector, segment_size=64)
            # self.cipher = blowfish.Cipher(self.key.encode('utf-8'))
            # self.cipher = Blowfish.new(self.key.encode('utf-8'), Blowfish.MODE_CFB)

    def blowfish_set_key(self, key: bytes, max_key_size=56):
        # Maximum key size in bytes for Blowfish is 56 bytes (448 bits)
        if len(key) > max_key_size:
            print(f"Key is longer than {max_key_size} bytes, truncating.")
            key = key[:max_key_size]  # Truncate the key to 56 bytes

        print(f"Final key length: {len(key)} bytes")
        return key

    def decrypt(self, data: bytearray):
        if self.key_exchange:
            # self.client.enc_server.
            from packet_processor.enc.packets.decrypt import Decrypt
            decrypt = Decrypt(self.client.enc_client)
            decrypt.create(data, self.client.forward_packet.account_id)

            self.client.enc_client.send(decrypt)
            pk = self.client.enc_client.socket.receive()
            if self.client.text_file is not None and not self.client.text_file.closed:
                self.client.text_file.write('<------')
                self.client.text_file.write('\n')
                self.client.text_file.write(to_hex_string(pk))
                self.client.text_file.write('\n')
            return pk

        server_payload = self.cipher.decrypt(data)
        if self.is_padding:
            server_payload = unpad(server_payload, Blowfish.block_size)
        memcpy(data, server_payload, len(server_payload), 0)
        return server_payload

    def encrypt(self, data: bytearray):
        if self.is_padding:
            data = pad(data, Blowfish.block_size)
        server_payload = self.cipher.encrypt(data)
        memcpy(data, server_payload, len(server_payload), 0)
        return server_payload

    def set_key(self, key: bytes):
        pass

    def set_ivs(self, iv_one: bytes, iv_two: bytes):
        self.iv_one = iv_one
        self.iv_two = iv_two

    def pad(self, data):
        return data + b'\x00' * (8 - len(data) % 8)

    def unpad(self, data):
        return data.rstrip(b'\x00')
