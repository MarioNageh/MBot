import math
import random
import threading

from constants import Coordinate


class Rectangle:
    max_allowed_jump = 14

    def __init__(self, top_left: Coordinate, bottom_right: Coordinate, top_right: Coordinate, bottom_left: Coordinate):
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.width = abs(self.bottom_right.x - self.top_left.x)
        self.height = abs(self.top_left.y - self.bottom_left.y)
        self.thread_local = threading.local()

    def is_within_bounds(self, x, y):
        return (self.top_left.x <= x <= self.bottom_right.x
                and self.top_left.y <= y <= self.bottom_right.y)

    def get_rnd_point_inside(self, x_center, y_center, min_dist=1, max_dist=14):
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        random.shuffle(directions)  # Add randomness to direction order

        '''
        Start from the maximum distance to the minimum distance, and iterate over all possible points
        '''
        for distance in range(max_dist, min_dist - 1, -1):
            for dx, dy in directions:
                x = x_center + dx * distance
                y = y_center + dy * distance

                # Ensure the point is within bounds
                if self.is_within_bounds(x, y):
                    point_to_jump = Coordinate(x, y)
                    actual_distance = Coordinate.distance_between_points(Coordinate(x_center, y_center), point_to_jump)

                    '''
                    Ensure the actual distance is within the min and max distance
                    '''
                    if min_dist <= actual_distance <= max_dist:
                        return point_to_jump

        '''
        if no point is found, return the center point
        '''
        return Coordinate(x_center, y_center)

    def get_point_inside_to_jump_to(self, current_position: Coordinate):
        max_value_decomposition = self.max_allowed_jump

        while True:
            rnd = self.get_rnd_point_inside_v2(current_position.x, current_position.y, 1, max_value_decomposition)
            distance = Coordinate.distance_between_points(current_position, rnd)
            if distance <= max_value_decomposition:
                return rnd

    def get_thread_local_random(self):
        if not hasattr(self.thread_local, 'random'):
            self.thread_local.random = random.Random()
        return self.thread_local.random

    def get_rnd_point_inside_v2(self, x_center, y_center, min_dist=1, max_dist=14):
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

        rnd = self.get_thread_local_random()
        rnd.shuffle(directions)  # Add randomness to direction order

        '''
        Try to find a point with a random distance within the range
        '''
        for _ in range(100):  # Number of trials to find a valid point
            distance = rnd.uniform(min_dist, max_dist)  # Random distance between min_dist and max_dist
            dx, dy = rnd.choice(directions)  # Random direction
            x = math.ceil(x_center + dx * distance)
            y = math.ceil(y_center + dy * distance)

            # Ensure the point is within bounds
            if self.is_within_bounds(x, y):
                point_to_jump = Coordinate(x, y)
                actual_distance = Coordinate.distance_between_points(Coordinate(x_center, y_center), point_to_jump)

                '''
                Ensure the actual distance is within the min and max distance
                '''
                if min_dist <= actual_distance <= max_dist:
                    return point_to_jump

        '''
        if no point is found, return the center point
        '''
        return Coordinate(x_center, y_center)