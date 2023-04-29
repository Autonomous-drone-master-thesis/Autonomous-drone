"""Module for the HumanTracker class."""

from dataclasses import dataclass
import math
from typing import Tuple, TYPE_CHECKING

import numpy as np

from .base_tracker import BaseTracker

if TYPE_CHECKING:
    from handlers import TelloHandler


@dataclass
class TrackerValues:
    """Dataclass for storing values used in tracking."""

    current_error_x: int
    current_error_y: int
    current_error_z: int
    forward_backward_velocity: int
    up_down_velocity: int
    yaw_velocity: int


# pylint: disable=R0903
class HumanTracker(BaseTracker):
    """Class for tracking humans."""

    def __init__(
        self,drone: "TelloHandler", target_distance: int, target_height: int, tracking_human_height: int
        ) -> None:
        super().__init__(drone)
        self.target_distance = target_distance # in cm
        self.target_height = target_height # in cm
        self.tracking_human_height = tracking_human_height # in cm
        self.image_width = 1280
        self.image_height = 720
        self.pid_gains = {"p": [0.15, 0.3, 0.1], "i": [0.1, 0.3, 0.01], "d": [0.2, 0.3, 0.1]}
        self.vertical_field_of_view = self._get_field_of_view() # in radians

    # pylint: disable=W0221
    def track(
        self,
        center: Tuple[int, int],
        previous_errors: Tuple[int, int, int],
        bbox_height: int,
        track: bool,
    ) -> Tuple[int, int]:
        x, y = center

        # Safety mechanism to prevent drone from moving when human detected but
        # not yet confirmed by user to track.
        if x != 0 and y != 0 and not track:
            self.drone.send_rc_control(0, 0, 0, 0)
            return 0, 0, 0

        previous_error_x, previous_error_y, previous_error_z = previous_errors

        current_error_x = x - self.image_width // 2

        yaw_velocity = self._calculate_yaw_velocity(current_error_x, previous_error_x)

        values = TrackerValues(
            current_error_x=current_error_x,
            current_error_y=0,
            current_error_z=0,
            forward_backward_velocity=0,
            up_down_velocity=0,
            yaw_velocity=yaw_velocity,
        )

        if x != 0 and y != 0:
            distance = self._calculate_distance(bbox_height)
            height = self._calculate_drone_height(y, distance)

            values.current_error_y = -(height - self.target_height)
            values.current_error_z = distance - self.target_distance

            values.up_down_velocity = self._calculate_up_down_velocity(
                values.current_error_y,
                previous_error_y
                )

            values.forward_backward_velocity = self._calculate_forward_backward_velocity(
                values.current_error_z, previous_error_z
            )

        self.drone.send_rc_control(
            0,
            values.forward_backward_velocity,
            values.up_down_velocity,
            values.yaw_velocity
            )

        return values.current_error_x, values.current_error_y, values.current_error_z

    def _calculate_yaw_velocity(self, current_error_x: int, previous_error_x: int) -> int:
        yaw_velocity = (
            self.pid_gains["p"][0] * current_error_x +
            self.pid_gains["d"][0] * (current_error_x - previous_error_x)
        )
        yaw_velocity = int(np.clip(yaw_velocity, -50, 50))
        return yaw_velocity

    def _calculate_up_down_velocity(self, current_error_y: int, previous_error_y: int) -> int:
        up_down_velocity = self.pid_gains["p"][2] * current_error_y + self.pid_gains["d"][2] * (
            current_error_y - previous_error_y
        )
        up_down_velocity = int(np.clip(up_down_velocity, -50, 50))
        return up_down_velocity

    def _calculate_forward_backward_velocity(
        self,
        current_error_z: int,
        previous_error_z: int
        ) -> int:
        forward_backward_velocity = (
            self.pid_gains["p"][1] * current_error_z +
            self.pid_gains["d"][1] * (current_error_z - previous_error_z)
            )
        forward_backward_velocity = int(np.clip(forward_backward_velocity, -50, 50))
        return forward_backward_velocity

    def _get_field_of_view(self) -> float:
        sensor_height = 3.6
        focal_length = 3.61
        return 2 * math.atan((sensor_height / 2) / focal_length)

    def _calculate_distance(self, bbox_height):
        distance = (self.tracking_human_height * self.image_height) / (
            2 * bbox_height * math.tan(self.vertical_field_of_view / 2)
        )
        return distance

    def _calculate_drone_height(self, center_y, distance):
        angle_to_bbox_bottom = (
            (self.image_height / 2 - center_y) *
            (self.vertical_field_of_view / self.image_height)
            )
        height_difference = math.tan(angle_to_bbox_bottom) * distance
        drone_height = self.tracking_human_height - height_difference
        return drone_height
