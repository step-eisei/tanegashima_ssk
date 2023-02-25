# 距離フェーズ
import class_distance
import class_motor
import subthread
import time
import math
import numpy as np

class Distance_phase:
    
    def __init__(self, distance=None, motor=None, subth=None):
        if distance == None: self.distance = class_distance.Distance()
        else:                self.distance = distance

        if motor == None:    self.motor = class_motor.Motor()
        else:                self.motor = motor
        
        if subth == None:
            self.subth = subthread.Subthread(distance=self.distance, motor=self.motor)
            self.subth.run()
        else:                self.subth = subth


    def run(self):
        self.subth.phase = 4
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
                    self.subth.record(comment="distance")
                    print("finished")
                    return 0
                else: 
                    print("forward")
                    self.motor.forward(duty, duty, 0.05, tick_dutymax=5)#距離に応じて前進
                    time.sleep(distance/20)
                    self.motor.changeduty(0,0)
            else:
                if(i <= 19):#その場で旋回してコーンを探す
                    print("rotate")
                    angle = 18*(i+1)
                    if angle > 180:
                        angle = angle - 360
                    if(i%2 == 0):
                        self.motor.rotate(angle,threshold= 3) # 左に旋回
                    else: 
                        self.motor.rotate(-angle,threshold= 3) # 右に旋回
                    i += 1
                else:# 現在位置から直進して離れてフェーズを離れる
                    self.motor.forward(20,20 ,0.1, tick_dutymax=5)
                    time.sleep(5)
                    self.motor.changeduty(0,0)
                    return -1

def main():
    try:
        distance = class_distance.Distance()
        motor = class_motor.Motor()
        subth = subthread.Subthread(distance=distance, motor=motor)
        subth.run()
        distance_phase = Distance_phase(distance=distance,motor=motor,subth=subth)
        distance_phase.run()
        distance_phase.motor.end()
    except KeyboardInterrupt:
        distance_phase.motor.end()
        print("\nInterrupted.")
    
if __name__ == "__main__":
    main()