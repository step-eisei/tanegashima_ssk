import RPi.GPIO as GPIO
import time

class Nicrom():
    def __init__(self, pin=22):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin,  GPIO.OUT)
        pass

    def heat(self, t=10):
        GPIO.output(self.pin, True)
        time.sleep(t)
        GPIO.output(self.pin, False)
    
    def end(self):
        GPIO.output(self.pin, False)
        GPIO.cleanup()

def main():
    nicrom = Nicrom(pin=22)

    try:
        print("start")
        nicrom.start(t=10)

        nicrom.end()
        print("end")
    except:
        nicrom.end()

if __name__ == "__main__":
    main()