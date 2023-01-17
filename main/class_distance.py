#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import RPi.GPIO as GPIO


class Distance:
    
    def __init__(self,TRIG,ECHO):
            self.TRIG = TRIG
            self.ECHO = ECHO
            pass

    def reading(self,sensor = 0):
        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            if sensor == 0:
                GPIO.setup(self.TRIG,GPIO.OUT)
                GPIO.setup(self.ECHO,GPIO.IN)
                GPIO.output(self.TRIG, GPIO.LOW)
                time.sleep(0.3)
                GPIO.output(self.TRIG, True)
                time.sleep(0.00001)
                GPIO.output(self.TRIG, False)
                while GPIO.input(self.ECHO) == 0:
                    signaloff = time.time()
                while GPIO.input(self.ECHO) == 1:
                    signalon = time.time()
                timepassed = signalon - signaloff
                distance = timepassed * 17000
                return distance
                GPIO.cleanup()
            else:
                print("Incorrect usonic() function varible.")
        except KeyboardInterrupt:
            GPIO.output(self.TRIG, False)
            GPIO.cleanup()


def main():
    while(True):
        distance = Distance(17,27)
        print(distance.reading())
        time.sleep(1)
    pass

if __name__ == "__main__":
    main()
    pass

data = [10, 11, 12, 14, 1000]
ave = np.mean(data)
max = 0
num = 0
for i in range(len(data)):
    if((ave-data[i])**2 > max):
        num = i
        max = (ave-data[i])**2
data = np.delete(data, num)
print(data)
data = np.mean(data)
