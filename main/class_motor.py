import RPi.GPIO as GPIO
import time
import random
import math
import class_geomag
# right = A, left = B

class Motor():
    def __init__(self, pwm=100, rightIN1=5, rightIN2=6, leftIN1=19, leftIN2=26, geomag=class_geomag.GeoMagnetic()):
        self.rightIN1 = rightIN1
        self.rightIN2 = rightIN2
        self.leftIN1 = leftIN1
        self.leftIN2 = leftIN2
        self.geomag = geomag
        self.duty_R_now = -1
        self.duty_L_now = -1
        
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
        self.duty_R_now = duty_R
        self.duty_L_now = duty_L
            
    def forward(self, duty_R, duty_L, time_sleep=0, time_all=0, tick_dutymax=0):
        if(time_sleep!=0):
            if(time_all!=0):
                loop_duty = int(time_all/time_sleep)
                for i in range(loop_duty):
                    self.changeduty((duty_R-self.duty_R_now)*(i+1)/loop_duty+self.duty_R_now, (duty_L-self.duty_L_now)*(i+1)/loop_duty+self.duty_L_now)
                    time.sleep(time_sleep)
            elif(tick_dutymax!=0):
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

    def rotate(self, angle=0, duty_R=10, duty_L=None, threshold_angle=10, time_sleep_constant=0.01):
        if(angle!=0):
            if(duty_L==None): duty_L = -duty_R
            self.geomag.get()
            theta_past = self.geomag.theta_absolute
            for i in range(3):
                if(angle>0): self.changeduty(duty_R, duty_L)
                else: self.changeduty(-duty_R, -duty_L)
                time.sleep(abs(time_sleep_constant*angle))
                self.changeduty(0, 0)
                for j in range(2):
                    self.geomag.get()
                    theta_now = self.geomag.theta_absolute
                    change_angle = self.angle_difference(theta_past, theta_now)
                    if(change_angle > angle-abs(threshold_angle) and change_angle < angle+abs(threshold_angle)): break
                    elif(change_angle==0): self.stack()
                    else: time_sleep_constant = time_sleep_constant*angle/change_angle
                    if(abs(time_sleep_constant*angle)<0.02):
                        if(angle>0): self.changeduty(-duty_R, -duty_L)
                        else: self.changeduty(duty_R, duty_L)
                        time.sleep(0.02)
                        self.changeduty(0, 0)
                    elif(abs(time_sleep_constant*angle)>3):
                        time_sleep_constant = 3/angle
                    else: break
            print("loop limit.")
        else: print("Error. angle is not defined.")
    
    def stack(self, duty_R=50, duty_L=50):
        while True:
            self.rotate(90, threshold_angle=20)
            for i in range(random.randint(1, 3)):
                self.forward(duty_R=random.randint(int(duty_R/2), duty_R), duty_L=random.randint(int(duty_L/2), duty_L), time_sleep=0.05, tick_dutymax=5)
                time.sleep(1)
                self.changeduty(0, 0)
                time.sleep(0.5)
            self.geomag.get()
            theta_past = self.geomag.theta_absolute
            self.rotate(90, threshold_angle=90)
            self.geomag.get()
            theta_now = self.geomag.theta_absolute
            if (self.angle_difference(theta_past, theta_now)<30): print("stack")
            else: break
            duty_R=-duty_R
            duty_L=-duty_L
    
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
        
        motor.rotate(angle=90)
        # モータ初期化
        motor.end()
        print("finish")

    except KeyboardInterrupt:
        motor.end()
        print("Interrupted")

if __name__ == "__main__":
    main()
