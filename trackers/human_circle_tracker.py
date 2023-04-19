from typing import Tuple

import numpy as np

from handlers import TelloHandler

class HumanCircler:
    def __init__(
        self,
        drone: TelloHandler,
        horizontal_focal_length: float = 443.61,
        vertical_focal_length: float = 591.48,
        target_distance: float = 1.5,
    ) -> None:
        self.drone = drone
        self.width, self.height = 1280, 720
        self.horizontal_focal_length = horizontal_focal_length
        self.vertical_focal_length = vertical_focal_length
        self.target_distance = target_distance

        self.pid = [0.15, 0.15, 0.1]

    def track(self, bbox: Tuple[int, int, int, int], previous_error: Tuple[int, int]) -> Tuple[int, int]:
        x1, y1, x2, y2 = bbox
        previous_error_x, previous_error_y = previous_error

        width = x2 - x1
        height = y2 - y1

        distance_x = self.horizontal_focal_length / width
        distance_y = self.vertical_focal_length / height

        pid_distance_ratio_x = self.target_distance / distance_x
        pid_distance_ratio_y = self.target_distance / distance_y

        adjusted_pid_x = [pid_gain * pid_distance_ratio_x for pid_gain in self.pid]
        adjusted_pid_y = [pid_gain * pid_distance_ratio_y for pid_gain in self.pid]

        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        error_x = center_x - self.width // 2
        error_y = center_y - self.height // 2

        yaw_velocity = int(
            adjusted_pid_x[0] * error_x + adjusted_pid_x[1] * (error_x - previous_error_x)
        )
        up_down_velocity = int(
            adjusted_pid_y[0] * error_y + adjusted_pid_y[1] * (error_y - previous_error_y)
        )

        circle_velocity = 15

        self.drone.send_rc_control(-circle_velocity, 0, up_down_velocity, yaw_velocity)

        return error_x, error_y