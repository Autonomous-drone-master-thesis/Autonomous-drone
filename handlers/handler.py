"""Module for the TelloHandler class."""
try:
    from djitellopy import Tello
except ImportError:
    Tello = None


class TelloHandler(Tello):
    """TelloHandler class is a wrapper class for the Tello class from the djitellopy library."""

    def connect_and_initiate(self) -> None:
        """Connects to the drone and initiates the drone to takeoff and hover at 25cm."""
        self.connect()
        self.streamon()

    def disconnect(self) -> None:
        """Disconnects from the drone and lands it."""
        self.streamoff()
        self.land()
