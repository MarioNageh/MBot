import ctypes
from ctypes import c_int, c_void_p, byref, POINTER

from cryptography.cryptography import Cryptography
from utils.helpers import memcpy, to_hex_string
import os


# check if os is windows
libcrypto = None
if os.name == 'nt':
    libcrypto = ctypes.CDLL(r'./libeay32.dll')
else:
    libcrypto = ctypes.CDLL(r'/usr/openssl/libcrypto.so.1.1')

# Set the argument and return types for the OpenSSL functions used
libcrypto.BF_cfb64_encrypt.argtypes = [POINTER(ctypes.c_ubyte), POINTER(ctypes.c_ubyte), c_int, c_void_p,
                                       POINTER(ctypes.c_ubyte), POINTER(c_int), c_int]
libcrypto.BF_set_key.argtypes = [c_void_p, c_int, POINTER(ctypes.c_ubyte)]
libcrypto.BF_set_key.restype = None

libcrypto.BF_cfb64_encrypt.argtypes = [
    POINTER(ctypes.c_ubyte),  # Input data
    POINTER(ctypes.c_ubyte),  # Output buffer
    c_int,  # Length of data
    c_void_p,  # Key schedule
    POINTER(ctypes.c_ubyte),  # IV
    POINTER(c_int),  # Num (passed by reference)
    c_int  # Encryption/decryption mode
]
libcrypto.BF_cfb64_encrypt.restype = None


class BlowfishAlgorithm:
    ECB = 0
    CBC = 1
    CFB64 = 2
    OFB64 = 3


class BFKeyStructure(ctypes.Structure):
    _fields_ = [
        ("P", ctypes.c_uint * 18),  # Array of 18 unsigned integers
        ("S", ctypes.c_uint * 1024)  # Array of 1024 unsigned integers
    ]


class GameCryptography(Cryptography):
    def __init__(self, algorithm: int, key: bytes, iv_one: bytes = None, iv_two: bytes = None):
        self._algorithm = algorithm
        self._encryptNum = c_int(0)
        self._decryptNum = c_int(0)

        self._key_schedule = BFKeyStructure()

        # Allocate unmanaged memory for key schedule
        self._key = ctypes.create_string_buffer(ctypes.sizeof(self._key_schedule))
        ctypes.memmove(self._key, ctypes.byref(self._key_schedule), ctypes.sizeof(self._key_schedule))

        # Initialize IVs
        self._encryptIv = (ctypes.c_ubyte * 8)() if iv_one is None else (ctypes.c_ubyte * 8)(*iv_one)
        self._decryptIv = (ctypes.c_ubyte * 8)() if iv_two is None else (ctypes.c_ubyte * 8)(*iv_two)
        self.set_key(key)

    def _generate_key_schedule(self, key: bytes):
        """Generate and return the Blowfish key schedule."""
        key_array = (ctypes.c_ubyte * len(key))(*key)
        libcrypto.BF_set_key(ctypes.cast(byref(self._key), c_void_p), len(key), key_array)


    def encrypt(self, data: bytearray) -> bytes:
        """Encrypt the given data using Blowfish."""
        out_ = (ctypes.c_ubyte * len(data))()  # Output buffer

        libcrypto.BF_cfb64_encrypt(
            (ctypes.c_ubyte * len(data))(*data),
            out_,
            len(data),
            ctypes.cast(byref(self._key), c_void_p),
            self._encryptIv,
            byref(self._encryptNum),
            1
        )
        memcpy(data, bytes(out_), len(data), 0)
        return bytes(out_)

    def decrypt(self, data: bytearray) -> bytes:
        """Decrypt the given data using Blowfish."""
        out_ = (ctypes.c_ubyte * len(data))()  # Output buffer

        libcrypto.BF_cfb64_encrypt(
            (ctypes.c_ubyte * len(data))(*data),
            out_,
            len(data),
            ctypes.cast(byref(self._key), c_void_p),
            self._decryptIv,
            byref(self._decryptNum),
            0
        )
        memcpy(data, bytes(out_), len(data), 0)
        return bytes(out_)

    def set_key(self, key: bytes):
        """Set the encryption/decryption key."""
        self._generate_key_schedule(key)

    def set_ivs(self, iv_one: bytes = None, iv_two: bytes = None):
        """Set the initialization vectors for encryption and decryption."""

        # Set encryption IV, use zeroed IV if not provided
        if iv_one is not None:
            ctypes.memmove(self._encryptIv, (ctypes.c_ubyte * 8)(*iv_one), 8)
        else:
            self._encryptIv = (ctypes.c_ubyte * 8)()

        # Set decryption IV, use zeroed IV if not provided
        if iv_two is not None:
            ctypes.memmove(self._decryptIv, (ctypes.c_ubyte * 8)(*iv_two), 8)
        else:
            self._decryptIv = (ctypes.c_ubyte * 8)()
