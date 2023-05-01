from djitellopy import Tello

tello = Tello()

try:
    tello.connect()
    tello.takeoff()
except Exception as e:
    print(e)
finally:
    tello.land()
