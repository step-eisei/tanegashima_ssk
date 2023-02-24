import datetime
import csv
import time
import class_motor
import class_nicrom
import class_distance
import class_geomag
import subthread

class Deploy():
    def __init__(self, motor=class_motor.Motor(), nicrom=class_nicrom.Nicrom(), dist_sens=class_distance.Distance(), mag=class_geomag.GeoMagnetic(), subthread=subthread.Subthread()):
        self.motor = motor
        self.nicrom = nicrom
        self.dist_sens = dist_sens
        self.mag = mag
        self.subthread = subthread
    
    def run(self, time_heat=10, duty=60, duty_calibrate=5, percent=5):
        self.subthread.phase = 1
        opend = False #距離センサでカプセルが取れたか確認
        moved = False #その後その場で回転して動けているか
        #最初は閉まってるかつ止まってる

        #-------展開検知---------
        while not(opend) or not(moved): #開くかつ動くまで
            count=0
            self.dist_sens.reading()
            distance = self.dist_sens.distance
            
            if distance >= 10:  #展開判定の閾値：１０
                count=count+1
            else:
                count=0
            
            if count>=3:
                opend = True 
            #距離センサによる展開

            if opend == False:
                self.nicrom.heat(t=time_heat)
                #開いてない⇒再加熱
            else:
                self.mag.get()
                ang0 = self.mag.theta_absolute
                #初期値

                self.motor.rotate(45, threshold_angle=45)
                self.mag.get()
                ang1 = self.mag.theta_absolute
                #移動後の位置取得

                if (ang1 - ang0) >= 10: #動けているか判定
                    moved == True
                else:
                    opend == False
        self.nicrom.end()
        self.subthread.record(comment="open")
        #両方Trueでループ終了

        ang0=0.0 #初期化
        ang1=0.0

        #-------前進,旋回によるスタック検知---------

        #前進
        self.motor.forward(duty, duty, 0.05, tick_dutymax=5)
        time.sleep(2)
        self.motor.changeduty(0, 0)
        # この時点で地磁気データが使えないので，スタック検知が難しいのが課題
        self.calibrate(duty_calibrate, p=percent)
        self.subthread.record(comment="deployment")
        print("deployment phase finish")

    def percentpick(self, listdata, p):
        n = int(len(listdata) *p/100)
        listdata = sorted(listdata) # 昇順
        min = listdata[n-1]
        max = listdata[len(listdata)-n]
        return max, min

    def calibrate(self, duty=10, p=5):
        self.mag_list = []

        self.motor.changeduty(duty, -duty)
        for i in range(300):
            self.mag.get()
            self.mag_list.append((self.mag.x, self.mag.y, self.mag.z))
            time.sleep(0.05)
        # csv save
        DIFF_JST_FROM_UTC = 9
        jp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
        self.recordname = 'mag/mag_' + str(jp_time).replace(' ', '_').replace(':', '-').replace('.', '_') + '.csv'
        with open(self.recordname, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["magx", "magy", "magz"])
            writer.writerows(self.mag_list)

        magxs = [self.mag_list[i][0] for i in range(len(self.mag_list))]
        magys = [self.mag_list[i][1] for i in range(len(self.mag_list))]
        magzs = [self.mag_list[i][2] for i in range(len(self.mag_list))]

        # 最大値，最小値の算出
        Xmax, Xmin = self.percentpick(magxs, p)
        Ymax, Ymin = self.percentpick(magys, p)
        Zmax, Zmin = self.percentpick(magzs, p)

        self.maxs = [Xmax, Ymax, Zmax]
        self.mins = [Xmin, Ymin, Zmin]

        self.mag.rads = [(self.maxs[i] - self.mins[i])/2 for i in range(3)]
        self.mag.aves = [(self.maxs[i] + self.mins[i])/2 for i in range(3)]

        self.mag.calibrated = True

def main():
    deploy_phase = Deploy()
    deploy_phase.run()

if __name__=="__main__":
    main()
