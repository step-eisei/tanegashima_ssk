import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(22,  GPIO.OUT)

try:
  s = time.time()
  GPIO.output(22, True)
  print("start")
  #ここの数字は実験次第
  time.sleep(10)
  GPIO.output(22, False)
  GPIO.cleanup()
  print("end time:10 sec.")
 
except:
  GPIO.output(22, False)
  GPIO.cleanup()
  e = time.time()
  print(f"end time:{e-s} sec.")
  
