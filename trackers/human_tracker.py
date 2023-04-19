from typing import Tuple

import numpy as np

from handlers import TelloHandler

class HumanTracker:
    """Class for tracking humans."""

    def __init__(
        self,
        drone: TelloHandler,
        horizontal_focal_length: float = 443.61,
        vertical_focal_length: float = 591.48,
        target_distance: float = 4.5,
        target_height: float = 2,
        real_height: float = 180

    ) -> None:
        """Initialize the HumanTracker object with the given drone.

        Args:
            drone (TelloHandler): the drone to control
        """
        self.drone = drone
        self.width, self.height = 1280, 720
        self.pid = [0.15, 0.15, 0.1]
        self.target_distance = target_distance
        self.horizontal_focal_length = horizontal_focal_length
        self.vertical_focal_length = vertical_focal_length
        self.target_height = target_height
        self.real_height = real_height

    def track(
        self,
        bbox_height: int,
        center: Tuple[int, int],
        previous_error: Tuple[int, int]
    ) -> Tuple[int, int]:
        x, y = center
        previous_error_x, previous_error_y = previous_error

        current_error_y = 0
        forward_backward_velocity = 0
        up_down_velocity = 0
        yaw_velocity = 0

        current_error_x = x - self.width // 2
        yaw_velocity = self.pid[0] * current_error_x + self.pid[1] * (current_error_x - previous_error_x)
        yaw_velocity = int(np.clip(yaw_velocity, -50, 50))

        if x != 0 and y != 0:
            current_error_y = y - self.height // 2
            up_down_velocity = -(self.pid[0] * current_error_y + self.pid[1] * (current_error_y - previous_error_y))
            up_down_velocity = int(np.clip(up_down_velocity, -25, 25))

            distance = (self.real_height * self.vertical_focal_length) / bbox_height
            distance_error = self.target_distance - distance
            forward_backward_velocity = int(np.clip(distance_error * self.pid[2], -20, 20))

            # Calculate angle between the drone and the person
            height_difference = self.target_height - (bbox_height * distance / self.vertical_focal_length)
            angle = self._calculate_angle(distance, height_difference)

            # Adjust up_down_velocity based on the angle
            if angle > 0:
                up_down_velocity = int(np.clip(angle * self.pid[0], -25, 25))
            else:
                up_down_velocity = -int(np.clip(abs(angle) * self.pid[0], -25, 25))

        self.drone.send_rc_control(0, forward_backward_velocity, up_down_velocity, yaw_velocity)

        return current_error_x, current_error_y

    def _calculate_angle(self, distance, height_difference):
        angle = np.arctan(height_difference / distance)
        return angle