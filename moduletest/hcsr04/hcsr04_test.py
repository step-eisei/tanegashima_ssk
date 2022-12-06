#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import RPi.GPIO as GPIO

def reading(sensor):
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        if sensor == 0:
            GPIO.setup(TRIG,GPIO.OUT)
            GPIO.setup(ECHO,GPIO.IN)
            GPIO.output(TRIG, GPIO.LOW)
            time.sleep(0.3)
            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)
            while GPIO.input(ECHO) == 0:
                signaloff = time.time()
            while GPIO.input(ECHO) == 1:
                signalon = time.time()
            timepassed = signalon - signaloff
            distance = timepassed * 17000
            return distance
            GPIO.cleanup()
        else:
            print("Incorrect usonic() function varible.")
    except KeyboardInterrupt:
        GPIO.output(TRIG, False)
        GPIO.cleanup()

def main():
    print(reading(0))
    pass

if __name__ == "__main__":
    TRIG = 17
    ECHO = 27
    main()
    pass
