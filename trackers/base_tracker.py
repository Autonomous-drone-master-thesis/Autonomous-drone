"""Module containing the BaseTracker class."""

from abc import ABC, abstractmethod
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from handlers import TelloHandler


class BaseTracker(ABC):
    """Abstract base class for tracking objects."""
    def __init__(self, drone: "TelloHandler") -> None:
        self.drone = drone

    @abstractmethod
    def track(self, center, previous_errors, *args) -> Tuple:
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
