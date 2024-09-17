import asyncio
import concurrent
import inspect
import threading
import time
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING

from utils.printer import TerminalPrinter

if TYPE_CHECKING:
    from main import Mbot


class MBotMainThread(Thread):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MBotMainThread, cls).__new__(cls)
        return cls._instance

    def __init__(self, name="MBotMainThread",event_loop=None):
        if getattr(self, '_initialized', False):
            return
        Thread.__init__(self, name=name)
        self.name = name
        self.mBots: list[Mbot] = []
        self._initialized = True
        self.event_loop = event_loop
        self.start()

    def add_bot(self, bot):
        self.mBots.append(bot)

    def re_login(self, bot):
        if bot.re_login:
            bot.printer.print_info(f"Reconnecting to the server [auth]")
            # check event loop
            if not self.event_loop:
                bot.printer.print_info(f"Event loop is not available")


            try:
                future = asyncio.run_coroutine_threadsafe(bot.login(), self.event_loop)
                # future.result(timeout=10)
            except concurrent.futures.TimeoutError:
                bot.printer.print_info("Timeout while trying to log in.")
                return False
            except Exception as e:
                bot.printer.print_info(f"Error scheduling re-login: {e}")
                return False

            return True
        return False

    def run(self):
        print("MBotMainThread started")
        while True:
            total_online = 0
            for bot in self.mBots[:]: # copy the list
                if not bot.forward_done and bot.connection_with_auth_server_timeout():
                    """
                    Means That Use Not Finish Authenticated Yet
                    and timeout happen
                    ** we need to relogin
                    """
                    if not self.re_login(bot):
                        self.mBots.remove(bot)

                    continue

                if bot.forward_done and not bot.connection_with_game_server_timeout():
                    """
                    Means That Use Not Finish With Game Server Yet
                    or disconnected from the game server
                    ** we need to relogin
                    """
                    if not self.re_login(bot):
                        self.mBots.remove(bot)
                    continue

                total_online += 1
            total_threads = threading.active_count()

            total_events =0
            if self.event_loop:
                total_events = len(asyncio.all_tasks(self.event_loop))
            TerminalPrinter.sprint_success(
                f"Total online: {total_online}/{len(self.mBots)}, Total loop events: {total_events}")
            active_threads = threading.enumerate()

            # for thread in active_threads:
            #     # Print the thread name
            #     print(f"Thread Name: {thread.name}")
            sleep(5)

