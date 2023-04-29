"""Module for the FaceTracker class."""

from dataclasses import dataclass
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
class FaceTracker(BaseTracker):
    """Class for tracking faces."""

    def __init__(self, drone: "TelloHandler") -> None:
        super().__init__(drone)
        self.width, self.height = 1280, 720
        self.area_range = [0.01, 0.02]
        self.pid = [0.15, 0.15, 0]

    # pylint: disable=W0221
    def track(
        self,
        center: Tuple[int, int],
        previous_errors: Tuple[int, int],
        area: float,
        track: bool,
    ) -> Tuple[int, int]:
        x, y = center

        # Safety mechanism to prevent drone from moving when face detected but
        # not yet confirmed by user to track.
        if x != 0 and y != 0 and not track:
            self.drone.send_rc_control(0, 0, 0, 0)
            return 0, 0, 0

        previous_error_x, previous_error_y = previous_errors

        current_error_x = x - self.width // 2

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
            values.current_error_y = y - self.height // 2
            values.up_down_velocity = self._calculate_up_down_velocity(
                values.current_error_y,
                previous_error_y
                )

            values.forward_backward_velocity = self._calculate_forward_backward_velocity(area)

        self.drone.send_rc_control(
            0,
            values.forward_backward_velocity,
            values.up_down_velocity,
            values.yaw_velocity
            )

        return values.current_error_x, values.current_error_y

    def _calculate_yaw_velocity(self, current_error_x: int, previous_error_x: int) -> int:
        yaw_velocity = (
            self.pid[0] * current_error_x +
            self.pid[1] * (current_error_x - previous_error_x)
            )
        yaw_velocity = int(np.clip(yaw_velocity, -50, 50))
        return yaw_velocity

    def _calculate_up_down_velocity(self, current_error_y: int, previous_error_y: int) -> int:
        up_down_velocity = -(
            self.pid[0] * current_error_y +
            self.pid[1] * (current_error_y - previous_error_y)
            )
        up_down_velocity = int(np.clip(up_down_velocity, -50, 50))
        return up_down_velocity

    def _calculate_forward_backward_velocity(self, area: float) -> int:
        if area > self.area_range[1]:
            forward_backward_velocity = -25
        elif area < self.area_range[0] and area != 0:
            forward_backward_velocity = 25
        else:
            forward_backward_velocity = 0
        return forward_backward_velocity
