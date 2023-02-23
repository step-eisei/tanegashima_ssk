# 距離フェーズ
import class_distance
import class_motor
import class_geomag
import subthread
import time
import math
import numpy as np
import csv

class Distance_phase:
    
    def __init__(self, motor, distance=None):#, geomag=None, subthread=subthread.Subthread()):
        if distance == None:
            self.distance = class_distance.Distance()
        else:
            self.distance = distance
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
            if(distance > 2 and distance < 500):
                i = 0
                print("detected")
                if(distance < 5): 
                    #self.subthread.record(comment="distance")
                    print("finished")
                    return 0
                else: 
                    print("forward")
                    self.motor.forward(duty, duty, 0.05, tick_dutymax=5)#距離に応じて前進
                    time.sleep(distance/10)
                    self.motor.changeduty(0,0)
                    #self.geomag.get()
            else:
                if(i <= 34):
                    print("rotate")
                    angle = 10*(i+1)
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
                    time.sleep(10)
                    self.motor.changeduty(0,0)
                    return -1

def main():
    with open('calibration_lsm303.csv', 'r') as f :# goal座標取得プログラムより取得
        reader = csv.reader(f)
        line = [row for row in reader]
        rads = [float(line[1][i]) for i in range(3)]
        aves = [float(line[2][i]) for i in range(3)]
    f.close()
    geomag=class_geomag.GeoMagnetic(True, rads, aves)
    distance_phase = Distance_phase(motor=class_motor.Motor(geomag=geomag))
    distance_phase.run()
    
if __name__ == "__main__":
    main()