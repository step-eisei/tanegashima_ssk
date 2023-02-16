# 距離フェーズ
import class_distance
import class_motor
import class_geomag
import subthread

class Distance_phase:
    
    def __init__(self, distance=class_distance.Distance(), motor=class_motor.Motor(), geomag=class_geomag.GeoMagnetic(), subthread=subthread.Subthread()):
        self.distance = distance
        self.motor = motor
        self.geomag = geomag
        self.subthread = subthread
    
    def run(self):
        self.subthread.phase = 4
        duty = 20
        i = 0
        while True:
            self.distance.reading()
            distance = self.distance.distance # get distance
            if(self.distance.distance > 2 and self.distance.distance < 200):
                b = self.distance.distance/10
                if(self.distance < 5): 
                    self.subthread.record(comment="distance")
                    return 0
                else: 
                    self.motor.changeduty(b, b)
                    self.motor.forward(10,10)#距離に応じて前進
                    self.geomag.get()
            else:
                if(i <= 34):
                    if(i%2 == 0):
                        self.motor.rotate(10*(i/2+1),threshold_angle = 5*(i/2+1)) # 右に10*(i/2+1)deg旋回
                    else: 
                        self.motor.rotate(-10*(i-1)/2,threshold_angle = 5*(i-1)/2) # 左に10*(i-1)/2deg旋回
                    i += 1
                else:
                    # ゴール角度算出
                    theta_gps = math.atan2(self.y, self.x) * 180/math.pi
                    # 機体正面を0として，左を正，右を負とした変数(-180~180)を作成
                    self.theta_relative = theta_gps + self.mag.theta_absolute + 90
                    if(self.theta_relative > 180): self.theta_relative -= 360
                    if(self.theta_relative < -180): self.theta_relative += 360
                    a = 180 - self.theta_relative
                    self.motor.rotate(a,threshold_angle = 30)# ゴールと逆向きに旋回
                    self.motor.forward(10,10 ,time_sleep = 0.1)# 1m直進
                    return -1

def main():
    distance_phase = Distance_phase()
    distance_phase.run()
    
if __name__ == "__main__":
    main()
    pass

