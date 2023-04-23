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
        self.width, self.height = 1280, 720
        self.area_range = [0.01, 0.02]
        self.pid = [0.15, 0.15, 0]

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
        previous_error_x, previous_error_y = previous_error

        forward_backward_velocity = 0
        up_down_velocity = 0
        yaw_velocity = 0

        current_error_y = y - self.height // 2
        current_error_x = x - self.width // 2

        yaw_velocity = self.pid[0] * current_error_x + self.pid[1] * (current_error_x - previous_error_x)
        yaw_velocity = int(np.clip(yaw_velocity, -50, 50))

        if x != 0 and y != 0:
            up_down_velocity = -(self.pid[0] * current_error_y + self.pid[1] * (current_error_y - previous_error_y))
            up_down_velocity = int(np.clip(up_down_velocity, -50, 50))

            if area > self.area_range[1]:
                forward_backward_velocity = -25
            elif area < self.area_range[0] and area != 0:
                forward_backward_velocity = 25

        self.drone.send_rc_control(0, forward_backward_velocity, up_down_velocity, yaw_velocity)

        return current_error_x, current_error_y