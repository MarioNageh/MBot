import time
from typing import List


class Event:
    def __init__(self, client, callback_function=None, periodic=False, interval=0):
        self.execute_time_after = 0
        self.client = client
        self.callback_function = callback_function
        self.periodic = periodic
        self.interval = interval
        self.is_finished = False
        self.last_execution_time = time.time()
        self.event_args = {}
        self.calls_count = 0

    def set_event_args(self, **kwargs):
        self.event_args = kwargs

    def add_event_args(self, **kwargs):
        self.event_args.update(kwargs)

    @staticmethod
    def create_event_from_callback(client, callback_function):
        return Event(client, callback_function=callback_function, periodic=callback_function.periodic,
                     interval=callback_function.interval)

    def is_event_ready(self):
        return time.time() - self.last_execution_time >= self.interval

    async def execute(self):

        if self.is_event_ready():
            if self.callback_function:
                try:
                    await self.callback_function(self, self.client)  # Execute the callback function
                except Exception as e:
                    raise e

            if self.periodic:
                self.last_execution_time = time.time()
            else:
                self.is_finished = True


class Kernel:
    def __init__(self):
        self.events: List[Event] = []  # A list to hold all events
        self.start_time = time.time()
        self.is_running = True

    def add_event(self, event: Event):
        """Add a new event to the kernel."""
        self.events.append(event)

    def remove_event(self, event: Event):
        """Remove an event from the kernel."""
        if event in self.events:
            self.events.remove(event)

    def clear_events(self):
        """Clear all events."""
        self.events.clear()

    def stop(self):
        self.is_running = False
        self.clear_events()

    def start(self):
        self.is_running = True

    async def execute_events(self):
        """Execute all events, removing those that are finished."""
        for event in self.events[:]:  # Copy the list to avoid modification during iteration
            if self.is_running:
                await event.execute()
                if event.is_finished:
                    self.remove_event(event)  # Remove the event if it's finished
            else:
                break

    def main_event(self):
        self.execute_events()
