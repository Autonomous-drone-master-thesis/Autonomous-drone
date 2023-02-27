import time
import cv2
import logging
from threading import Thread
from djitellopy import Tello

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(filename)s - %(lineno)d - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def main():
    tello = Tello()
    tello.connect()

    try:
        tello.streamon()
        frame_read = tello.get_frame_read()

        time.sleep(3)

        while True:
            img = cv2.cvtColor(frame_read.frame, cv2.COLOR_RGB2BGR)
            cv2.imshow("Streaming", img)

    except Exception as e:
        logger.error('Error: %s', e)

    finally:
        tello.streamoff()


if __name__ == "__main__":
    main()
