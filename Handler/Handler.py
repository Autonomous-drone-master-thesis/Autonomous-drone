from djitellopy import Tello

class TelloHandler(Tello):
    def connect_and_initiate(self) -> None:
        self.connect()
        self.streamon()
        self.takeoff()
        self.send_rc_control(0, 0, 25, 0)

    def disconnect(self) -> None:
        self.land()