import class_motor
import time

class Test:
    def __init__(self, motor=None): #, subthread=None):
        if motor == None:     self.motor = class_motor.Motor()
        else:                 self.motor = motor
        self.motor.geomag.calibrated = True
        self.geomag = self.motor.geomag

    def angle_difference(self, from_angle, to_angle):
        angle = to_angle-from_angle
        if(angle<-180): return angle+360
        elif(angle>180): return angle-360
        return angle
    
    def forward(self, forward_time): 
        self.geomag.get()
        angle_before = self.geomag.theta_absolute

        self.motor.forward(30, 25, time_sleep=0.05, tick_dutymax=5)
        time.sleep(forward_time)
        self.motor.forward(10, 10, 0.1, tick_dutymax=5)
        self.motor.changeduty(0,0)
        time.sleep(1)

        self.geomag.get()
        angle_after = self.geomag.theta_absolute
        angle_diff = self.angle_difference(angle_before, angle_after)
        print(angle_diff)
        c = 10
        if angle_diff > 0:
            angle_diff += forward_time * c
        elif angle_diff < 0:
            angle_diff -= forward_time * c
        angle_diff += 10

        print(-angle_diff)
        self.motor.rotate(-angle_diff)

test = Test()
test.forward(1)