from djitellopy import Tello
from djitellopy import TelloException

tello = Tello()

try:
    tello.connect()
    tello.takeoff()
except TelloException as e:
    print(e)
finally:
    tello.land()
