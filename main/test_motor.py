import RPi.GPIO as GPIO
import time
import random
import math
import class_motor
# right = A, left = B


def main():
    t = 3
    duty = 30
    try:
        print("setup")
        motor = class_motor.Motor()

        print("forward start")
        motor.forward(duty, duty, 0.05, tick_dutymax=5)
        time.sleep(t)
        
        print("duty5")
        motor.forward(5, 5, 0.05, tick_dutymax=5)
        time.sleep(t)
        print("stop")
        motor.changeduty(0, 0)
        time.sleep(t)
        
        # print("forward fin.\nreverse start")
        # motor.forward(-duty, -duty, 0.05, tick_dutymax=5)
        # time.sleep(t)
        
        # print("stop")
        # motor.changeduty(0, 0)
        # time.sleep(t)
        # print("reverse fin.")
        
        # motor.rotate(angle=90)
        # モータ初期化
        motor.end()
        print("finish")

    except KeyboardInterrupt:
        motor.end()
        print("Interrupted")

if __name__ == "__main__":
    print("main")
    main()
