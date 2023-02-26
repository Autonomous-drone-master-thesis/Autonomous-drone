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

class VideoRecorder:
    def __init__(self, drone):
        self.drone = drone
        self.frame_read = self.drone.get_frame_read()
        self.video_filename = 'video.avi'
        self.recording = False
        self.video_writer = None

    def start_recording(self):
        self.recording = True
        height, width, _ = self.frame_read.frame.shape
        self.video_writer = cv2.VideoWriter(self.video_filename, cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height))
        self.recorder_thread = Thread(target=self.record)
        logger.info('Start recording video to %s', self.video_filename)
        self.recorder_thread.start()

    def stop_recording(self):
        self.recording = False
        logger.info('Stop recording video to %s', self.video_filename)
        if self.recorder_thread.is_alive():
            self.recorder_thread.join()
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None

    def record(self):
        while self.recording:
            self.video_writer.write(self.frame_read.frame)
            time.sleep(1 / 30)

def main():
    tello = Tello()
    tello.connect()

    video_recorder = VideoRecorder(tello)

    try:
        tello.streamon()

        # Start recording
        video_recorder.start_recording()

        tello.takeoff()

        tello.move_up(100)

        tello.rotate_counter_clockwise(360)
        
        tello.land()

    except Exception as e:
        logger.error('Error: %s', e)

    finally:
        # Stop recording
        video_recorder.stop_recording()

        tello.streamoff()
        tello.end()


if __name__ == "__main__":
    main()
