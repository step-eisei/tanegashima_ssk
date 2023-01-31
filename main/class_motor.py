import RPi.GPIO as GPIO
import time

class Motor():
    def __init__(self, pwm=50, rightIN1=18, rightIN2=23, leftIN1=13, leftIN2=24):
        self.rightIN1 = rightIN1
        self.rightIN2 = rightIN2
        self.leftIN1 = leftIN1
        self.leftIN2 = leftIN2
        
        GPIO.setmode(GPIO.BCM) # GPIOnを指定するように設定
        GPIO.setup(rightIN1, GPIO.OUT)
        GPIO.setup(rightIN2, GPIO.OUT)
        GPIO.setup(leftIN1, GPIO.OUT)
        GPIO.setup(leftIN2, GPIO.OUT)
        self.pwms = {}
        self.pwms["rightIN1"] = GPIO.PWM(self.rightIN1, pwm) # pin, Hz
        self.pwms["rightIN2"] = GPIO.PWM(self.rightIN2, pwm) # pin, Hz
        self.pwms["leftIN1"] = GPIO.PWM(self.leftIN1, pwm) # pin, Hz
        self.pwms["leftIN2"] = GPIO.PWM(self.leftIN2, pwm) # pin, Hz
        
        self.pwms["rightIN1"].start(0)
        self.pwms["rightIN2"].start(0)
        self.pwms["leftIN1"].start(0)
        self.pwms["leftIN2"].start(0)
    
    def changeduty(self, duty_R, duty_L):
        if duty_R > 0:
            self.pwms["rightIN1"].ChangeDutyCycle(abs(duty_R))
            self.pwms["rightIN2"].ChangeDutyCycle(0)
        elif duty_R < 0:
            self.pwms["rightIN1"].ChangeDutyCycle(0)
            self.pwms["rightIN2"].ChangeDutyCycle(abs(duty_R))
        else:
            self.pwms["rightIN1"].ChangeDutyCycle(0)
            self.pwms["rightIN2"].ChangeDutyCycle(0)

        if duty_L > 0:
            self.pwms["leftIN1"].ChangeDutyCycle(abs(duty_L))
            self.pwms["leftIN2"].ChangeDutyCycle(0)
        elif duty_L < 0:
            self.pwms["leftIN1"].ChangeDutyCycle(0)
            self.pwms["leftIN2"].ChangeDutyCycle(abs(duty_L))
        else:
            self.pwms["leftIN1"].ChangeDutyCycle(0)
            self.pwms["leftIN2"].ChangeDutyCycle(0)
            

    def end(self):
        self.pwms["rightIN1"].stop()
        self.pwms["rightIN2"].stop()
        self.pwms["leftIN1"].stop()
        self.pwms["leftIN2"].stop()
        GPIO.output(self.rightIN1, False)
        GPIO.output(self.rightIN2, False)
        GPIO.output(self.leftIN1, False)
        GPIO.output(self.leftIN2, False)
        GPIO.cleanup()


def main():
    t = 3
    duty = 60
    try:
        print("setup")
        motor = Motor()

        print("forward start")
        for i in range(10):
            duty_new = int(duty/10*(i+1))
            motor.changeduty(duty_new, duty_new)
            time.sleep(0.1)
        time.sleep(t)
        
        print("stop")
        """
        for i in range(10):
            duty_new = int(duty*(1-(i+1)/10))
            motor.changeduty(duty_new, duty_new)
            time.sleep(0.1)
        """
        motor.changeduty(0, 0)
        time.sleep(t)
        
        print("forward fin.\nreverse start")
        for i in range(10):
            duty_new = int(-duty/10*(i+1))
            motor.changeduty(duty_new, duty_new)
            time.sleep(0.1)
        time.sleep(t)
        
        print("stop")
        """
        for i in range(10):
            duty_new = int(-duty*(1-(i+1)/10))
            motor.changeduty(duty_new, duty_new)
            time.sleep(0.1)
        """
        motor.changeduty(0, 0)
        time.sleep(t)
        print("reverse fin.")
        
        # モータ初期化
        motor.end()
        print("finish")

    except KeyboardInterrupt:
        motor.end()
        print("Interrupted")

if __name__ == "__main__":
    main()
