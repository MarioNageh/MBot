from typing import Optional

from client.client import Client
from constants import Coordinate
from data.items_holder import ItemsHolder
from data.sob_npc_controller import SobNpcController


class Player:

    def __init__(self,
                 client: Client = None
                 , user_id=None
                 , look_interface=None
                 , hair=None
                 , money=None
                 , user_cps=None
                 , name=None
                 , profession=None
                 ):
        client.main_app.printer.printer_data.user_name = name
        client.main_app.printer.printer_data.user_id = user_id

        self.client = client
        self.user_id = user_id
        self.look_interface = look_interface
        self.hair = hair
        self.money = money
        self.user_cps = user_cps
        self.name = name
        self.profession = profession
        self.map_id = 0
        self.map_x = 0
        self.map_y = 0
        self._position = Coordinate(0, 0)

        self.item_holder: ItemsHolder = ItemsHolder(client)
        self.sobNpcController: SobNpcController = SobNpcController(client)
        self.player_has_use_gate_to_teleport = False

        self.player_finding_his_way = False
        self.target_coordinates: Optional[Coordinate] = None
        self.last_target_coordinates: Optional[Coordinate] = None
        self.target_object = None
        self.path = None
        self.is_attacking = False



        self.invalid_coordinates = False
        self.step_counter = 0

    def __str__(self):
        return (f"Player {self.name} with user_id {self.user_id} has {self.money} money and {self.user_cps} "
                f"cps in Map {self.map_id} at position {self.map_x}, {self.map_y}")

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value: Coordinate):
        self._position = value
        self.map_x = value.x
        self.map_y = value.y
        self.step_counter += 1

    def set_position(self, map_id, map_x, map_y):
        self.map_id = map_id
        self.map_x = map_x
        self.map_y = map_y
        self._position = Coordinate(map_x, map_y)
        self.step_counter += 1

    def update_position(self, direction: int):
        delta_x = [0, -1, -1, -1, 0, 1, 1, 1]
        delta_y = [1, 1, 0, -1, -1, -1, 0, 1]
        idx = direction % 8
        x = self.map_x
        y = self.map_y
        self.map_x += delta_x[idx]
        self.map_y += delta_y[idx]
        self._position = Coordinate(self.map_x, self.map_y)
        self.step_counter += 1


    def is_archer(self):
        return 40 <= self.profession <= 45

    def is_warrior(self):
        return 20 <= self.profession <= 25
