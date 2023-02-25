from djitellopy import Tello
from djitellopy import TelloException


def main() -> None:
    tello = Tello()

    try:
        tello.connect()
        tello.takeoff()
        for _ in range(4):
            tello.move_forward(20)
            tello.rotate_clockwise(90)
    except TelloException as e:
        print(e)
    finally:
        tello.land()


if __name__ == "__main__":
    main()
