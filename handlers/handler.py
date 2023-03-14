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
    
    def takeoff_and_hover(self) -> None:
        """Takes off and hovers at 35cm."""
        self.takeoff()
        self.send_rc_control(0, 0, 25, 0)

    def disconnect(self) -> None:
        """Disconnects from the drone and lands it."""
        self.send_rc_control(0, 0, 0, 0)
        # self.streamoff()
        self.land()
