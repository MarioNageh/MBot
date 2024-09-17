import ctypes
import time
from datetime import datetime


def get_current_time_hms() -> str:
    now = datetime.now()
    return now.strftime("%H:%M:%S:%f")


def get_current_time_stamp(player_id: int) -> int:
    # TODO Include player_id in the timestamp
    return ctypes.c_uint(round(time.time() * 1000)).value
