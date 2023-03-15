"""Module for the FaceTracker class."""
from typing import Tuple

try:
    import numpy as np
except ImportError:
    np = None

from handlers import TelloHandler


# pylint: disable=R0903
class FaceTracker:
    """Class for tracking faces."""

    def __init__(self, drone: TelloHandler) -> None:
        """Initialize the FaceTracker object with the given drone.

        Args:
            drone (TelloHandler): the drone to control
        """
        self.drone = drone
        self.area_range = [0.03, 0.05]
        self.pid = [0.25, 0.25, 0]
        self.width = 1280
        self.height = 720

    def track(self, area: float, center: Tuple[int, int], previous_error: Tuple[int, int]) -> Tuple[int, int]:
        """Track the face.

        Args:
            area (float): Area of the face
            center (Tuple[int, int]): Center of the face
            previous_error (Tuple[int, int]): Previous error (x and y)

        Returns:
            Tuple[int, int]: Current error (x and y)
        """
        x, y = center

        left_right_velocity = 0
        forward_backward_velocity = 0
        up_down_velocity = 0
        yaw_velocity = 0

        current_error_x = x - self.width // 2
        left_right_velocity = self.pid[0] * current_error_x + self.pid[1] * (current_error_x - previous_error[0])
        left_right_velocity = int(np.clip(left_right_velocity, -100, 100))

        current_error_y = y - self.height // 2
        up_down_velocity = self.pid[0] * current_error_y + self.pid[1] * (current_error_y - previous_error[1])
        up_down_velocity = int(np.clip(up_down_velocity, -100, 100))

        if area > self.area_range[1]:
            forward_backward_velocity = -10
        elif area < self.area_range[0] and area != 0:
            forward_backward_velocity = 10

        self.drone.send_rc_control(left_right_velocity, forward_backward_velocity, up_down_velocity, yaw_velocity)

        return current_error_x, current_error_y
