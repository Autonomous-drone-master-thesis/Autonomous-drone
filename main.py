import time
import cv2
import numpy as np
from djitellopy import Tello


class Drone:
    def __init__(self):
        self.tello = Tello()

    def run(self):
        self.tello.connect()

        self.tello.streamoff()
        time.sleep(2)
        self.tello.streamon()
        time.sleep(5)

        while True:
            frame = cv2.cvtColor(self.tello.get_frame_read().frame, cv2.COLOR_RGB2BGR)
            frame = cv2.resize(frame, (360, 240))

            cv2.imshow("Tello", frame)

            cv2.waitKey(1)


def main():
    drone = Drone()
    drone.run()


if __name__ == "__main__":
    main()
