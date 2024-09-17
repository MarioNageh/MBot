from constants import Coordinate


class SobNpc:
    def __init__(self, sob_uuid: int, max_health: int, health: int, x: int, y: int, mesh: int, flag: int,
                 sob_type: int):
        self.sob_uuid = sob_uuid
        self.max_health = max_health
        self.health = health
        self.x = x
        self.y = y
        self.mesh = mesh
        self.flag = flag
        self.sob_type = sob_type

    @property
    def position(self):
        return Coordinate(self.x, self.y)

    def __str__(self):
        return f"[SpawnSob] sob_uuid: {self.sob_uuid}, max_health: {self.max_health}, health: {self.health}, x: {self.x}, y: {self.y}, mesh: {self.mesh}, flag: {self.flag}, sob_type: {self.sob_type}"
