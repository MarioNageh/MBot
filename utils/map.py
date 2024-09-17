import enum
import heapq
import threading
import time

from constants import Coordinate
from packets.game import Tick
from utils.helpers import monitor_fun_execution_time
from utils.reader import Reader
import sys


class MapPointType(enum.Enum):
    Valid = 0
    Invalid = 1

    def __str__(self):
        return self.name


class Point:
    def __init__(self, x, y, flag: MapPointType, floor_type, altitude):
        self.x = x
        self.y = y
        self.flag = flag
        self.floor_type = floor_type
        self.altitude = altitude
        # A* algorithm
        self.g_cost = float('inf')
        self.h_cost = float('inf')
        self.parent = None

    def reset(self):
        self.g_cost = float('inf')
        self.h_cost = float('inf')
        self.parent = None

    @property
    def valid_point(self):
        return self.flag == MapPointType.Valid

    def f_cost(self):
        return self.g_cost + self.h_cost

    def __lt__(self, other):
        return self.f_cost() < other.f_cost()

    def __str__(self):
        return f'({self.x}, {self.y}), {self.flag})'


class Map:

    @monitor_fun_execution_time("Map")
    def __init__(self, file):
        self.file = open(file, 'rb')
        buffer = self.file.read()
        self.reader = Reader(buffer)
        self.reader.move_cursor_to(268)
        self.width = self.reader.read_int_32()
        self.height = self.reader.read_int_32()
        self.points = []
        for i in range(0, self.height):
            row = []
            for j in range(0, self.width):
                x = j
                y = i
                flag = MapPointType(self.reader.read_int_16())
                floor_type = self.reader.read_int_16()
                altitude = self.reader.read_int_16()
                point = Point(x, y, flag, floor_type, altitude)
                row.append(point)
            self.reader.read_int_32()
            self.points.append(row)
        self._lock = threading.Lock()

    def get_neighbors(self, point):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for direction in directions:
            nx, ny = point.x + direction[0], point.y + direction[1]
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbor = self.points[ny][nx]
                if neighbor.flag == MapPointType.Valid:
                    neighbors.append(neighbor)
        return neighbors

    def heuristic(self, point, end):
        return abs(point.x - end.x) + abs(point.y - end.y)

    def reconstruct_path(self, end_point):
        path = []
        current = end_point
        while current:
            path.append(Coordinate(current.x, current.y))
            current = current.parent
        return path[::-1]

    def check_time(self, start_time):
        current_time = time.time()
        if current_time - start_time > 3:
            return True
        return False

    @monitor_fun_execution_time("A* Algorithm")
    def a_star(self, start_coords, end_coords):
        # copy self.points
        start_time = time.time()
        with self._lock:
            if self.check_time(start_time):
                return None

            for row in self.points:
                for point in row:
                    point.reset()

            start_point = self.points[start_coords[1]][start_coords[0]]
            end_point = self.points[end_coords[1]][end_coords[0]]

            open_set = []
            heapq.heappush(open_set, start_point)

            start_point.g_cost = 0
            start_point.h_cost = self.heuristic(start_point, end_point)

            while open_set:
                if self.check_time(start_time):
                    return None

                current_point = heapq.heappop(open_set)

                if current_point == end_point:
                    return self.reconstruct_path(end_point)

                for neighbor in self.get_neighbors(current_point):
                    if self.check_time(start_time):
                        return None

                    tentative_g_cost = current_point.g_cost + 1

                    if tentative_g_cost < neighbor.g_cost:
                        neighbor.parent = current_point
                        neighbor.g_cost = tentative_g_cost
                        neighbor.h_cost = self.heuristic(neighbor, end_point)

                        if neighbor not in open_set:
                            heapq.heappush(open_set, neighbor)

            return None
