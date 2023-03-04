"""Module for the TelloHandler class."""
try:
    from djitellopy import tello
except ImportError:
    tello = None


class TelloHandler(tello):
    """TelloHandler class is a wrapper class for the Tello class from the djitellopy library."""

    def connect_and_initiate(self) -> None:
        """Connects to the drone and initiates the drone to takeoff and hover at 25cm."""
        self.connect()
        self.streamon()
        self.takeoff()
        self.send_rc_control(0, 0, 25, 0)

    def disconnect(self) -> None:
        """Disconnects from the drone and lands it."""
        self.land()
