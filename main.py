import time, cv2
from threading import Thread
import logging

from djitellopy import Tello, BackgroundFrameRead
from djitellopy import TelloException

HANDLER = logging.StreamHandler()
FORMATTER = logging.Formatter('[%(levelname)s] %(filename)s - %(lineno)d - %(message)s')
HANDLER.setFormatter(FORMATTER)

LOGGER = logging.getLogger('main')
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)


def main() -> None:
    tello = Tello()

    try:
        tello.connect()
        tello.streamon()
        frame_read = tello.get_frame_read()
        
        video = VideoRecorder(frame_read)
        recorder = Thread(target=video.start)
        recorder.start()
        
        tello.takeoff()
        for _ in range(4):
            tello.move_forward(20)
            tello.rotate_clockwise(90)
            cv2.imwrite("picture.png", frame_read.frame)
            LOGGER.info("Picture saved")
    except TelloException as e:
        print(e)
    finally:
        tello.land()
        
        video.keepRecording = False
        recorder.join()

class VideoRecorder:
    
    def __init__(self, frame_read: BackgroundFrameRead) -> None:
        self.frame_read = frame_read
        self.keepRecording = True
        self.video = None
        
    def start(self) -> None:
        height, width, _ = self.frame_read.frame.shape
        video = cv2.VideoWriter('video.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height))

        while self.keepRecording:
            video.write(self.frame_read.frame)
            time.sleep(1 / 30)

        video.release()
        LOGGER.info("Video saved")


if __name__ == "__main__":
    main()
