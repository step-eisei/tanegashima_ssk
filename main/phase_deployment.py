
import time
import class_motor
import class_nicrom
import class_distance
import class_geomag

def percentpick(listdata, p):
    n = int(len(listdata) *p/100)
    listdata = sorted(listdata) # 昇順
    min = listdata[n-1]
    max = listdata[len(listdata)-n]
    return max, min

class Deploy():
    def __init__(self, motor, nicrom, dist_sens, mag):
        self.motor = motor
        self.nicrom = nicrom
        self.dist_sens = dist_sens
        self.mag = mag
    
    def run(self):
        opend = False #距離センサでカプセルが取れたか確認
        moved = False #その後その場で回転して動けているか
        #最初は閉まってるかつ止まってる

        #-------展開検知---------
        while not(opend) or not(moved): #開くかつ動くまで
            self.dist_sens.reading()
            distance = self.dist_sens.distance
            if distance >= 100: opend = True
            #カメラによる展開

            if opend == False:
                self.nicrom.heat(t=10)
                #開いてない⇒再加熱

            if opend == True:
                self.mag.get()
                ang0 = self.mag.theta_absolute
                #初期値

                self.rotate(10)
                self.mag.get()
                ang1 = self.mag.theta_absolute
                #移動後の位置取得

                if (ang1 - ang0) >= 5: #動けているか判定
                    moved == True
                else:
                    opend == False

                self.rotate(-10)
        #両方Trueでループ終了

        ang0=0.0 #初期化
        ang1=0.0

        #-------前進,旋回によるスタック検知---------
        while True:
            duty=60

            #前進
            for i in range (10): 
                duty_new = int(duty/10*(i+1))
                self.motor.changeduty(duty_new, duty_new)
                time.sleep(0.1)
            
            time.sleep(2)

            #旋回
            self.mag.get()
            ang0 = self.mag.theta_absolute
            #初期値

            self.rotate(10)
            self.mag.get()
            ang1 = self.mag.theta_absolute

            if (ang1-ang0)<=5: #動けてなかったら
                print("stack")
                return
            else:
                self.rotate(-10)
                break
        
        self.calibrate()
        print("deployment phase finish")
    
    def rotate(self, angle):
        if angle > 0:
            duty = 20
        else:
            duty = -20
        t = abs(duty) / 765 * angle

        self.motor.changeduty(duty, -duty)
        time.sleep(t)
        self.motor.changeduty(0,0)
    
    def calibrate(self):
        duty = 20
        t = duty/765
        mag_list = []

        self.motor.changeduty(duty, -duty)
        total = 0      
        while total < t * 365:
            self.mag.get()
            mag_list.append((self.mag.x, self.mag.y, self.mag.z))
            time.sleep(t)
            total += t
        
        magxs = [self.maglist[i][0] for i in range(len(self.maglist))]
        magys = [self.maglist[i][1] for i in range(len(self.maglist))]
        magzs = [self.maglist[i][2] for i in range(len(self.maglist))]

        # 最大値，最小値の算出
        p = 5 # 上位何%をpickするか
        Xmax, Xmin = percentpick(magxs)
        Ymax, Ymin = percentpick(magys)
        Zmax, Zmin = percentpick(magzs)

        self.maxs = [Xmax, Ymax, Zmax]
        self.mins = [Xmin, Ymin, Zmin]

        self.mag.rads = [self.maxs[i] - self.mins[i] for i in range(3)]
        self.mag.aves = [self.maxs[i] + self.mins[i] for i in range(3)]

def main():
    motor = class_motor.Motor()
    nicrom = class_nicrom.Nicrom()
    dist_sens = class_distance.Distance()
    mag = class_geomag.GeoMagnetic()
    deploy_phase = Deploy(motor, nicrom, dist_sens, mag)
    deploy_phase.run()

if __name__=="__main__":
    main()