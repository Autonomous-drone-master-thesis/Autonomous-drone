import math
from typing import Tuple

import numpy as np

from handlers import TelloHandler


class HumanTracker:
    """Class for tracking humans."""

    def __init__(
        self,
        drone: TelloHandler,
        target_distance: float = 4.5,
        target_height: float = 2,
        real_height: float = 180

    ) -> None:
        """Initialize the HumanTracker object with the given drone.

        Args:
            drone (TelloHandler): the drone to control
        """
        self.drone = drone
        self.image_width = 920
        self.image_height = 720
        self.pid = [0.15, 0.15, 0.1]
        self.target_distance = target_distance
        self.real_human_height = 180  # in cm
        self.sensor_height = 3.6  # in mm
        self.focal_length = 3.61  # in mm
        self.vertical_field_of_view = 2 * \
            math.atan((self.sensor_height / 2) /
                      self.focal_length)  # in radians
        self.target_height = target_height
        self.real_height = real_height

    def track(
        self,
        bbox_height: int,
        center: Tuple[int, int],
        previous_error: Tuple[int, int]
    ) -> Tuple[int, int]:
        x, y = center
        current_error_y = 0
        current_error_x = x - self.image_width // 2

        if x != 0 and y != 0:
            distance = self._calculate_distance(bbox_height)
            print({"distance": distance, "height": self._calculate_drone_height(
                center[1], distance)})

        return current_error_x, current_error_y

    def _calculate_distance(self, bbox_height):
        distance = (self.real_height * self.image_height) / \
            (2 * bbox_height * math.tan(self.vertical_field_of_view / 2))
        return distance

    def _calculate_drone_height(self, center_y, distance):
        angle_to_bbox_bottom = (self.image_height / 2 - center_y) * \
            (self.vertical_field_of_view / self.image_height)
        height_difference = math.tan(angle_to_bbox_bottom) * distance
        drone_height = self.real_human_height - height_difference
        return drone_height
