from DJITelloPy import Tello
from DJITelloPy import TelloException

tello = Tello()

try:
    tello.connect()
    tello.takeoff()
except TelloException as e:
    print(e)
finally:
    tello.land()