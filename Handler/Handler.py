from djitellopy import Tello


class TelloHandler(Tello):
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
