"""Module for the FaceTracker class."""

from typing import Tuple

import numpy as np

from .base_tracker import BaseTracker, TrackerValues


# pylint: disable=R0903
class FaceTracker(BaseTracker):
    """Class for tracking faces."""

    def __init__(self) -> None:
        super().__init__()
        self.area_range = [0.01, 0.02]
        self.pid = [0.15, 0.15, 0]

    # pylint: disable=W0221
    def track(
        self,
        center: Tuple[int, int],
        previous_errors: Tuple[int, int],
        area: float,
        track: bool,
    ) -> Tuple[Tuple[int, int], Tuple[int, int, int, int]]:
        """
        Method for tracking faces.
        :param center: center of the face
        :param previous_errors: previous errors
        :param area: area of the face
        :param track: whether to track or not
        :return: previous errors and commands to be sent to the drone
        """
        center_x, center_y = center
        commands = (0, 0, 0, 0)

        # Safety mechanism to prevent drone from moving when face detected but
        # not yet confirmed by user to track.
        if center_x != 0 and center_y != 0 and not track:
            return (0, 0), commands

        previous_error_x, previous_error_y = previous_errors

        current_error_x = center_x - self.image_width // 2

        yaw_velocity = self._calculate_yaw_velocity(current_error_x, previous_error_x)

        values = TrackerValues(
            current_error_x=current_error_x,
            current_error_y=0,
            current_error_z=0,
            forward_backward_velocity=0,
            up_down_velocity=0,
            yaw_velocity=yaw_velocity,
        )

        if center_x != 0 and center_y != 0:
            values.current_error_y = center_y - self.image_height // 2
            values.up_down_velocity = self._calculate_up_down_velocity(
                values.current_error_y,
                previous_error_y
                )

            values.forward_backward_velocity = self._calculate_forward_backward_velocity(area)

        commands = (
            0,
            values.forward_backward_velocity,
            values.up_down_velocity,
            values.yaw_velocity
            )

        return (values.current_error_x, values.current_error_y), commands

    def _calculate_yaw_velocity(self, current_error_x: int, previous_error_x: int) -> int:
        """
        Method for calculating the yaw velocity.
        :param current_error_x: The current error in the x direction.
        :param previous_error_x: The previous error in the x direction.
        :return: The yaw velocity.
        """
        yaw_velocity = (
            self.pid[0] * current_error_x +
            self.pid[1] * (current_error_x - previous_error_x)
            )
        yaw_velocity = int(np.clip(yaw_velocity, -50, 50))
        return yaw_velocity

    def _calculate_up_down_velocity(self, current_error_y: int, previous_error_y: int) -> int:
        """
        Method for calculating the up/down velocity.
        :param current_error_y: The current error in the y direction.
        :param previous_error_y: The previous error in the y direction.
        :return: The up/down velocity.
        """
        up_down_velocity = -(
            self.pid[0] * current_error_y +
            self.pid[1] * (current_error_y - previous_error_y)
            )
        up_down_velocity = int(np.clip(up_down_velocity, -50, 50))
        return up_down_velocity

    def _calculate_forward_backward_velocity(self, area: float) -> int:
        """
        Method for calculating the forward/backward velocity.
        :param area: The area of the face.
        :return: The forward/backward velocity.
        """
        if area > self.area_range[1]:
            forward_backward_velocity = -25
        elif area < self.area_range[0] and area != 0:
            forward_backward_velocity = 25
        else:
            forward_backward_velocity = 0
        return forward_backward_velocity
