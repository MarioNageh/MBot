from constants import Coordinate
from data.sob_npc import SobNpc
from oop.patterns.singleton_meta import SingletonMeta


class SobNpcController(metaclass=SingletonMeta):
    def __init__(self, client):
        self.sob_npc = []

    def add_sob_npc(self, sob_npc: SobNpc):
        self.sob_npc.append(sob_npc)

    def remove_sob_npc(self, sob_npc: SobNpc):
        self.sob_npc.remove(sob_npc)

    def clear_screen(self):
        self.sob_npc.clear()

    def get_nearest_sob_npc(self, coords: Coordinate):
        min_distance = 0xffffff
        nearest_sob_npc = None
        for sob_npc in self.sob_npc:
            distance = Coordinate.distance_between_points(coords, sob_npc.position)
            if distance < min_distance:
                min_distance = distance
                nearest_sob_npc = sob_npc
        return nearest_sob_npc
