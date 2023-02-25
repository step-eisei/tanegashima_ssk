import RPi.GPIO as GPIO
import time
import random
import math
import class_geomag
import csv
# right = A, left = B

class Motor():
    def __init__(self, pwm=100, rightIN1=5, rightIN2=6, leftIN1=16, leftIN2=13, geomag=None):
        self.rightIN1 = rightIN1
        self.rightIN2 = rightIN2
        self.leftIN1 = leftIN1
        self.leftIN2 = leftIN2
        if geomag == None:
            with open ('calibration_lsm303.csv', 'r') as f :# goal座標取得プログラムより取得
                reader = csv.reader(f)
                line = [row for row in reader]
                rads = [float(line[1][i]) for i in range(3)]
                aves = [float(line[2][i]) for i in range(3)]
            f.close()
            self.geomag = class_geomag.GeoMagnetic(True, rads, aves)
        else: self.geomag = geomag
        self.geomag.calibrated = True
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
        if(duty_R != 0 and self.duty_R_now == 0): duty_R = 5
        else: duty_R = self.duty_R_now
        if(duty_L != 0 and self.duty_L_now == 0): duty_L = 5
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
    
    def rotate(self, angle, duty=18, threshold=3.0):
        self.geomag.get()
        angle_new = self.geomag.theta_absolute
        angle_diff = angle
        angle_target = angle_new + angle
        if angle_target > 180:
            angle_target -= 360
        elif angle_target < -180:
            angle_target += 360
        
        time_const = 0.01
        total = 20

        print(f"target:{angle_target}")

        try:
            for i in range(total):
                if angle_diff > 0:
                    self.changeduty(duty_R=duty, duty_L=-duty)
                else:
                    self.changeduty(duty_R=-duty, duty_L=duty)
                
                sleep_time = time_const * min(abs(angle_diff),30)

                time.sleep(sleep_time)
                self.changeduty(0,0)
                time.sleep(0.5)

                angle_old = angle_new
                self.geomag.get()
                angle_new = self.geomag.theta_absolute

                angle_changed = self.angle_difference(angle_old, angle_new)
                angle_diff = self.angle_difference(angle_new, angle_target)
                
                overshoot = abs(angle_changed)-abs(angle_diff)
                duty = duty - int(overshoot/10)
                duty = min(max(duty, 10),20)
                #print(f"now:{angle_new}")
                #print(f"diff:{angle_diff}")
                #print("")

                if -threshold < angle_diff < threshold:
                    break
            print(f"now:{angle_new}")
            print(f"diff:{angle_diff}")
        except KeyboardInterrupt:
            self.changeduty(0,0)
            print("\nKeyboardInterrupt")
        
        print(f"count:{i}")
        self.changeduty(0,0)
    
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
    duty = 30
    try:
        print("setup")
        motor = Motor()

        motor.rotate(40, threshold=1.0)
        return 

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
        print("\nInterrupted")

if __name__ == "__main__":
    print("main")
    main()
