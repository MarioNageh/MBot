from abc import ABC, abstractmethod


class Cryptography(ABC):
    def __init__(self):
        self.key_exchange = False

    @abstractmethod
    def encrypt(self, data: bytes):
        pass

    @abstractmethod
    def decrypt(self, data: bytes):
        pass

    @abstractmethod
    def set_key(self, key: bytes):
        pass

    @abstractmethod
    def set_ivs(self, iv_one: bytes, iv_two: bytes):
        pass
