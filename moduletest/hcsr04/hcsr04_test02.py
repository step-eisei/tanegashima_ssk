#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import RPi.GPIO as GPIO

def reading(sensor):
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
            waiting_time = time.time()
            if(time.time()-waiting_time > 2):
                print("reception error.")
                break

        timepassed = signalon - signaloff
        distance = timepassed * 17000
        return distance
        GPIO.cleanup()
    else:
        print("Incorrect usonic() function varible.")

def main():
    while(True):
        try:
            print(reading(0))
            time.sleep(1)
        except KeyboardInterrupt:
            GPIO.output(TRIG, False)
            GPIO.cleanup()
            break
    print("program fin.")

if __name__ == "__main__":
    TRIG = 17
    ECHO = 27
    main()
    pass
import RPi.GPIO as GPIO

def reading():
    GPIO.setwarnings(False)
     
    GPIO.setmode(GPIO.BCM)
    TRIG = 17
    ECHO = 27
    try:
        while True:
            try:
                GPIO.setup(TRIG,GPIO.OUT)
                GPIO.setup(ECHO,GPIO.IN)
                GPIO.output(TRIG, GPIO.LOW)
                time.sleep(0.3)
                
                GPIO.output(TRIG, True)
                time.sleep(0.00001)
                GPIO.output(TRIG, False)
        
                while GPIO.input(ECHO) == 0: signaloff = time.time()
                
                while GPIO.input(ECHO) == 1: signalon = time.time()
        
                timepassed = signalon - signaloff
                distance = timepassed * 17000
                print(distance)
            except: print(0)
    except KeyboardInterrupt:
        GPIO.cleanup()
         
if __name__ == "__main__":
    reading()
