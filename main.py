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
        self.tello.stream_on()

        frame_read = self.tello.get_frame_read()

        while i < 1000:
            frame = cv2.cvtColor(frame_read.frame, cv2.COLOR_RGB2BGR)
            frame = np.rot90(frame)
            frame = np.flipud(frame)

            cv2.imshow("Tello", frame)

            i += 1

        self.tello.end()


def main():
    drone = Drone()
    drone.run()


if __name__ == "__main__":
    main()
