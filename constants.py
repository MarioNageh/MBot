import dataclasses
import random
from math import sqrt, ceil, tan


@dataclasses.dataclass
class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def coord(self):
        return self.x, self.y

    @staticmethod
    def distance_between_points(p1, p2):
        return ceil(sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2))

    def __repr__(self):
        return f"Coordinate({self.x}, {self.y})"

    def __str__(self):
        return f"Coordinate({self.x}, {self.y})"

    @staticmethod
    def get_direction(from_point, to_point):
        delta_x = to_point.x - from_point.x
        delta_y = to_point.y - from_point.y
        # Horizontal or Vertical Movement
        if delta_x == 0:
            if delta_y > 0:
                return 0
            else:
                return 4
        elif delta_y == 0:
            if delta_x > 0:
                return 6
            else:
                return 2

        if delta_x < 0:
            delta_x = -1
        else:
            delta_x = 1

        if delta_y < 0:
            delta_y = -1
        else:
            delta_y = 1

        theta = tan(delta_x / delta_y)
        delta_sum = delta_y + delta_x
        if theta > 0:
            if delta_sum > 0:
                return 7
            else:
                return 3
        else:
            if delta_y > 0:
                return 1
            else:
                return 5

    @staticmethod
    def get_next_point(from_point, to_point, max_distance=12):
        delta_x = to_point.x - from_point.x
        delta_y = to_point.y - from_point.y

        distance = Coordinate.distance_between_points(from_point, to_point)
        if distance == 0:
            return from_point  # from_point and to_point are the same

        # If the distance is greater than max_distance, adjust the step size
        if distance > max_distance:
            step_x = delta_x * (max_distance / distance)
            step_y = delta_y * (max_distance / distance)
        else:
            step_x = delta_x
            step_y = delta_y

        next_x = from_point.x + round(step_x)
        next_y = from_point.y + round(step_y)

        return Coordinate(next_x, next_y)

    @staticmethod
    def get_randomized_direction(from_point, to_point):
        delta_x = to_point.x - from_point.x
        delta_y = to_point.y - from_point.y

        # Introduce randomness in delta_x and delta_y
        random_factor_x = random.uniform(-0.5, 0.5)
        random_factor_y = random.uniform(-0.5, 0.5)
        delta_x += random_factor_x
        delta_y += random_factor_y

        # Horizontal or Vertical Movement
        if delta_x == 0:
            if delta_y > 0:
                return 0
            else:
                return 4
        elif delta_y == 0:
            if delta_x > 0:
                return 6
            else:
                return 2

        # Adjust for direction
        if delta_x < 0:
            delta_x = -1
        else:
            delta_x = 1

        if delta_y < 0:
            delta_y = -1
        else:
            delta_y = 1

        # Calculate theta and use it for determining direction
        try:
            theta = tan(delta_x / delta_y)
        except ZeroDivisionError:
            theta = float('inf')  # Handle division by zero if needed

        delta_sum = delta_y + delta_x
        if theta > 0:
            if delta_sum > 0:
                return 7
            else:
                return 3
        else:
            if delta_y > 0:
                return 1
            else:
                return 5
class SobNpcToSearch:
    data = [
        # Coordinate(450, 388), 430	380
        # Coordinate(430, 380),

        Coordinate(450, 388),
        Coordinate(451, 367),
        Coordinate(428, 388),
        Coordinate(428, 368),

        #

        #
        #
        # Coordinate(449, 389),
        # Coordinate(449, 367),
        # Coordinate(428, 389),
        # Coordinate(428, 367),
    ]


class ConstantItems:
    TwinCityGate = 1060020


class ConstantShops:
    ShoppingMall = 2888


class Maps:
    TwinCity = 1002










#New BF Key wal1dyous4bpr0te