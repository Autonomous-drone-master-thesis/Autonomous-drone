import cv2


def get_frames(video_source):
    capture = cv2.VideoCapture(video_source)
    while capture.isOpened():
        success, frame = capture.read()
        if not success:
            break
        yield frame
    capture.release()
