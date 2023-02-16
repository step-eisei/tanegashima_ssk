import RPi.GPIO as GPIO
import time
import random
import math
# right = A, left = B

class Motor():
    def __init__(self, pwm=100, rightIN1=6, rightIN2=5, leftIN1=13, leftIN2=16):
        self.rightIN1 = rightIN1
        self.rightIN2 = rightIN2
        self.leftIN1 = leftIN1
        self.leftIN2 = leftIN2
        self.duty_R_now = -1
        self.duty_L_now = -1
        
        GPIO.setmode(GPIO.BCM) # GPIOnを指定するように設定
        GPIO.setup(self.rightIN1, GPIO.OUT)
        GPIO.setup(self.rightIN2, GPIO.OUT)
        GPIO.setup(self.leftIN1, GPIO.OUT)
        GPIO.setup(self.leftIN2, GPIO.OUT)
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
        self.duty_R_now = duty_R
        self.duty_L_now = duty_L

    def currentblock(self, duty_R, duty_L):
        # prevent Overcurrent
        if(duty_R != 0 and self.duty_R_now == 0): duty_R = 1
        else: duty_R = self.duty_R_now
        if(duty_L != 0 and self.duty_L_now == 0): duty_L = 1
        else: duty_L = self.duty_L_now
        self.changeduty(duty_R, duty_L)
        time.sleep(1)

    def forward(self, duty_R, duty_L, time_sleep=0, time_all=0, tick_dutymax=0):
        if(time_sleep!=0):
            if(time_all!=0):
                self.currentblock(duty_R, duty_L)
                loop_duty = int(time_all/time_sleep)
                for i in range(loop_duty):
                    self.changeduty((duty_R-self.duty_R_now)*(i+1)/loop_duty+self.duty_R_now, (duty_L-self.duty_L_now)*(i+1)/loop_duty+self.duty_L_now)
                    time.sleep(time_sleep)
            elif(tick_dutymax!=0):
                self.currentblock(duty_R, duty_L)
                loop_duty = math.ceil(max(abs(duty_R-self.duty_R_now), abs(duty_L-self.duty_L_now))/tick_dutymax)
                for i in range(loop_duty):
                    self.changeduty((duty_R-self.duty_R_now)*(i+1)/loop_duty+self.duty_R_now, (duty_L-self.duty_L_now)*(i+1)/loop_duty+self.duty_L_now)
                    time.sleep(time_sleep)
            else: print("Error. Define time_all or tick_dutymax.")
        else: print("Error. time_sleep is not defined.")

    def angle_difference(self, from_angle, to_angle):
        angle = to_angle-from_angle
        if(angle<-180): return angle+360
        elif(angle>180): return angle-360
        return angle
    
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
    duty = 30
    try:
        print("setup")
        motor = Motor()

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
