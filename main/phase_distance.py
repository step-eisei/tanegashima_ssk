# 距離フェーズ
import class_distance
import class_motor
import class_geomag

class Distance_phase:
    
    def __init__(self, distance=class_distance.Distance(17, 27), motor=class_motor.Motor(pwm=200, 18, 23, 13, 24), geomag=class_geomag.Geomagnetic()):
        self.distance = distance
        self.motor = motor
        self.geomag = geomag
    
    def run(self):
        self.motor.duty = 10 # 低
        # goal角度取得
        i = 0
        while True:
            # get distance
            if(self.distance.distance > 2 and self.distance.distance < 200):
                #地磁気取得
                #ゴール角度更新
                if(0m判定): return 0
                else: #距離に応じて前進
            else:
                if(i <= 34):
                    if(i%2 == 0): # 右に10*(i/2+1)deg旋回
                    else: # 左に10*(i-1)/2deg旋回
                    i+=1
                else:
                    # ゴールと逆向きに旋回
                    # 1m直進
                    return -1

def main():
    distance_phase = Distance_phase()
    distance_phase.run()
    
if __name__ == "__main__":
    main()
    pass
