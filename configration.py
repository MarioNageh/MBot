import ast

from dotenv import load_dotenv
import os

from utils.helpers import get_env_bool


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def convert_string_blowfish_key_to_bytearray(self, key):
        x = ast.literal_eval(key)
        key = bytes(x)
        return key

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        load_dotenv()
        server_padding = os.getenv('SERVER_PADDING')
        game_ip = os.getenv('GAME_IP')
        game_port = int(os.getenv('GAME_PORT', 5816), 10)
        blowfish_key = os.getenv('BLOWFISH_KEY', [])
        blowfish_key = self.convert_string_blowfish_key_to_bytearray(blowfish_key)
        sql_injection = get_env_bool('SQL_INJECTION_MODE', False)

        encryption_server_ip = os.getenv('ENCRYPTION_SERVER_IP')
        encryption_server_port = os.getenv('ENCRYPTION_SERVER_PORT')

        self.server_padding = server_padding
        self.game_ip = game_ip
        self.game_port = game_port
        self.blowfish_key = blowfish_key
        self.sql_injection = sql_injection
        self.encryption_server_ip = encryption_server_ip
        self.encryption_server_port = encryption_server_port
        self.server_name = os.getenv('SERVER_NAME')

    @staticmethod
    def server_name():
        return Config().server_name
