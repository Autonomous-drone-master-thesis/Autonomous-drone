import numpy as np

from ..Handler import TelloHandler

class FaceTracker:
    def __init__(self, drone: 'TelloHandler') -> None:
        self.drone = drone
        self.area_range = [0.03, 0.05]
        self.pid = [0.3, 0.3, 0]
        self.width = 360
        self.height = 240
    
    def track(self, area, center, previous_error):
        x, y = center
        forward_backward = 0
        current_error = x - self.width // 2
        speed = self.pid[0] * current_error + self.pid[1] * (current_error - previous_error)
        speed = int(np.clip(speed, -100, 100))
        if area > self.area_range[1]:
            forward_backward = -10
        elif area < self.area_range[0] and area != 0:
            forward_backward = 10
        self.drone.send_rc_control(0, forward_backward, 0, speed)

        return current_error