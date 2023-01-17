import RPi.GPIO as GPIO
import time

class Motor():
    def __init__(self, pwm=50, AIN1=18, AIN2=23, BIN1=13, BIN2=24):
        self.AIN1 = AIN1
        self.AIN2 = AIN2
        self.BIN1 = BIN1
        self.BIN2 = BIN2
        
        GPIO.setmode(GPIO.BCM) # GPIOnを指定するように設定
        GPIO.setup(AIN1, GPIO.OUT)
        GPIO.setup(AIN2, GPIO.OUT)
        GPIO.setup(BIN1, GPIO.OUT)
        GPIO.setup(BIN2, GPIO.OUT)
        self.pwms = {}
        self.pwms["AIN1"] = GPIO.PWM(self.AIN1, pwm) # pin, Hz
        self.pwms["AIN2"] = GPIO.PWM(self.AIN2, pwm) # pin, Hz
        self.pwms["BIN1"] = GPIO.PWM(self.BIN1, pwm) # pin, Hz
        self.pwms["BIN2"] = GPIO.PWM(self.BIN2, pwm) # pin, Hz
        
        self.pwms["AIN1"].start(0)
        self.pwms["AIN2"].start(0)
        self.pwms["BIN1"].start(0)
        self.pwms["BIN2"].start(0)
    
    def changeduty(self, duty_R, duty_L):
        if duty_R > 0:
            self.pwm["AIN1"].ChangeDutyCycle(abs(duty_R))
            self.pwm["AIN2"].ChangeDutyCycle(0)
        elif duty_R < 0:
            self.pwm["AIN1"].ChangeDutyCycle(0)
            self.pwm["AIN2"].ChangeDutyCycle(abs(duty_R))
        else:
            self.pwm["AIN1"].ChangeDutyCycle(0)
            self.pwm["AIN2"].ChangeDutyCycle(0)

        if duty_L > 0:
            self.pwm["BIN1"].ChangeDutyCycle(abs(duty_L))
            self.pwm["BIN2"].ChangeDutyCycle(0)
        elif duty_L < 0:
            self.pwm["BIN1"].ChangeDutyCycle(0)
            self.pwm["BIN2"].ChangeDutyCycle(abs(duty_L))
        else:
            self.pwm["BIN1"].ChangeDutyCycle(0)
            self.pwm["BIN2"].ChangeDutyCycle(0)
            

    def end(self):
        self.pwmAIN1.stop()
        self.pwmAIN2.stop()
        self.pwmBIN1.stop()
        self.pwmBIN2.stop()
        GPIO.output(self.AIN1, False)
        GPIO.output(self.AIN2, False)
        GPIO.output(self.BIN1, False)
        GPIO.output(self.BIN2, False)
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