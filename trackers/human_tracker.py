import math
from typing import Tuple, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from handlers import TelloHandler



class HumanTracker:
    """Class for tracking humans."""

    def __init__(
        self,
        drone: "TelloHandler",
        target_distance: int = 500,
        target_height: int = 400,
        real_height: int = 180

    ) -> None:
        """Initialize the HumanTracker object with the given drone.

        Args:
            drone (TelloHandler): the drone to control
        """
        self.drone = drone
        self.image_width = 1280
        self.image_height = 720
        self.pid_gains = {
            "p": [0.15, 0.3, 0.1],
            "i": [0.1, 0.3, 0.01],
            "d": [0.2, 0.3, 0.1]
        }
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
        previous_errors: Tuple[int, int, int]
    ) -> Tuple[int, int]:
        x, y = center
        previous_error_x, previous_error_y, previous_error_z = previous_errors

        current_error_x = 0
        current_error_y = 0
        current_error_z = 0

        forward_backward_velocity = 0
        up_down_velocity = 0
        yaw_velocity = 0

        current_error_x = x - self.image_width // 2

        yaw_velocity = self.pid_gains["p"][0] * current_error_x + \
                self.pid_gains["d"][0] * (current_error_x - previous_error_x)
        yaw_velocity = int(np.clip(yaw_velocity, -50, 50))

        if x != 0 and y != 0:
            distance = self._calculate_distance(bbox_height)
            height = self._calculate_drone_height(y, distance)

            current_error_y = -(height - self.target_height)
            current_error_z = distance - self.target_distance

            forward_backward_velocity = self.pid_gains["p"][1] * current_error_z + \
                self.pid_gains["d"][1] * (current_error_z - previous_error_z)
            forward_backward_velocity = int(
                np.clip(forward_backward_velocity, -50, 50))

            up_down_velocity = self.pid_gains["p"][2] * current_error_y + \
                self.pid_gains["d"][2] * (current_error_y - previous_error_y)
            up_down_velocity = int(np.clip(up_down_velocity, -50, 50))

        self.drone.send_rc_control(
            0, forward_backward_velocity, up_down_velocity, yaw_velocity)
        #TODO: Remove print statements
        print(f"forward_backward_velocity: {forward_backward_velocity} up_down_velocity: {up_down_velocity} yaw_velocity: {yaw_velocity}")
        print("----------------------------------")
        return current_error_x, current_error_y, current_error_z

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
