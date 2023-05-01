"""Module containing the BaseTracker class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple

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
class BaseTracker(ABC):
    """Abstract base class for tracking objects."""
    def __init__(self) -> None:
        self.image_width = 1280
        self.image_height = 720

    @abstractmethod
    def track(self, center, previous_errors, *args) -> Tuple[Tuple, Tuple[int, int, int, int]]:
        """
        Abstract method for tracking objects.
        """

    @abstractmethod
    def _calculate_yaw_velocity(self, current_error_x: int, previous_error_x: int) -> int:
        """
        Abstract method for calculating the yaw velocity.
        """

    @abstractmethod
    def _calculate_up_down_velocity(self, current_error_y: int, previous_error_y: int) -> int:
        """
        Abstract method for calculating the up/down velocity.
        """

    @abstractmethod
    def _calculate_forward_backward_velocity(self) -> int:
        """
        Abstract method for calculating the forward/backward velocity.
        """
