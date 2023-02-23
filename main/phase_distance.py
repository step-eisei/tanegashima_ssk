# 距離フェーズ
import class_distance
import class_motor
import class_geomag
import subthread
import time
import math
import numpy as np

class Distance_phase:
    
    def __init__(self, distance=None, motor=None):#, geomag=None, subthread=subthread.Subthread()):
        if distance == None:
            self.distance = class_distance.Distance()
        else:
            self.distance = distance
        if motor == None:
            self.motor = class_motor.Motor()
        else:
            self.motor = motor
        """
        if geomag == None:
            self.geomag = self.motor.geomag
        else:
            self.geomag = geomag
        """
        #self.subthread = subthread
    
    def run(self):
        #self.subthread.phase = 4
        duty = 10
        i = 0
        print("start")
        while True:
            print("read")
            self.distance.reading()
            distance = self.distance.distance # get distance
            print(f"distance:{distance}")
            if(distance > 2 and distance < 200):
                i = 0
                print("detected")
                if(distance < 20): 
                    #self.subthread.record(comment="distance")
                    print("finished")
                    return 0
                else: 
                    print("forward")
                    self.motor.forward(duty, duty, 0.05, tick_dutymax=5)#距離に応じて前進
                    time.sleep(distance/20)
                    self.motor.changeduty(0,0)
                    #self.geomag.get()
            else:
                if(i <= 19):
                    print("rotate")
                    angle = 18*(i+1)
                    if angle > 180:
                        angle = angle - 360
                    if(i%2 == 0):
                        self.motor.rotate(angle,threshold= 3) # 左に旋回
                    else: 
                        self.motor.rotate(-angle,threshold= 3) # 右に旋回
                    i += 1
                else:
                    """
                    # ゴール角度算出
                    theta_gps = math.atan2(self.y, self.x) * 180/math.pi
                    # 機体正面を0として，左を正，右を負とした変数(-180~180)を作成
                    self.theta_relative = theta_gps + self.mag.theta_absolute + 90
                    if(self.theta_relative > 180): self.theta_relative -= 360
                    if(self.theta_relative < -180): self.theta_relative += 360
                    a = 180 - self.theta_relative
                    """
                    #self.motor.rotate(180, threshold=5)# ゴールと逆向きに旋回
                    self.motor.forward(20,20 ,0.1, tick_dutymax=5)# 1m直進
                    time.sleep(5)
                    self.motor.changeduty(0,0)
                    return -1

def main():
    distance_phase = Distance_phase()
    distance_phase.run()
    
if __name__ == "__main__":
    main()