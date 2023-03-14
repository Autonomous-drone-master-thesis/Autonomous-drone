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

    def track(self, area: float, center: Tuple[int, int], previous_error: int) -> int:
        """Track the face.

        Args:
            area (float): Area of the face
            center (Tuple[int, int]): Center of the face
            previous_error (int): Previous error

        Returns:
            int: Current error
        """
        x, y = center
        print(x,y)
        forward_backward = 0
        up_down = 0
        current_error = x - self.width // 2
        speed = self.pid[0] * current_error + self.pid[1] * (current_error - previous_error)
        speed = int(np.clip(speed, -75, 75))
        if area > self.area_range[1]:
            forward_backward = -10
        elif area < self.area_range[0] and area != 0:
            forward_backward = 10
        if y != 0:
            if y > self.height // 2:
                up_down = 10
            elif y < self.height // 2:
                up_down = -10

        self.drone.send_rc_control(0, forward_backward, up_down, speed)

        return current_error
