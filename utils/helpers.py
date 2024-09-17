import os
import random
import string
import time

from utils.printer import TerminalPrinter


def get_random_string(size: int) -> str:
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(size))
    return result_str


def create_byte_array_of_string_length(strings: str, length: int) -> bytearray:
    b: bytearray = bytearray(length)
    for i, v in enumerate(strings):
        b[i] = ord(v)
    return b


def memcpy(destination: bytearray, source: bytearray, length: int, offset: int) -> None:
    for i in range(length):
        destination[i] = source[i + offset]


def memcpy(destination: bytearray, source: bytes, length: int, offset: int) -> None:
    for i in range(length):
        destination[i] = source[i + offset]


def to_hex_string(b, is_no_space=False):
    if is_no_space:
        return (''.join(' {:02x}'.format(x) for x in b))[1::]
    return (''.join(' {:02x}'.format(x) for x in b))[1::]


def get_env_bool(var_name, default=False):
    value = os.getenv(var_name, str(default))
    return value.lower() == 'true'


def monitor_fun_execution_time(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            diff = end - start
            TerminalPrinter.sprint_success(f"{name} Loaded in {diff:.2f} seconds")
            return result
        return wrapper
    return decorator
