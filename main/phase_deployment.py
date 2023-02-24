import datetime
import csv
import time
import class_motor
import class_nicrom
import class_distance
import class_geomag
import subthread

class Deploy():
    def __init__(self, motor=None, nicrom=None, dist_sens=None, mag=None, subth=None):
        if motor == None:     self.motor = class_motor.Motor()
        else:                 self.motor = motor

        if nicrom == None:    self.nicrom = class_nicrom.Nicrom()
        else:                 self.nicrom = nicrom

        if dist_sens == None: self.dist_sens = class_distance.Distance()
        else:                 self.dist_sens = dist_sens

        self.geomag = self.motor.geomag
        
        """
        if subth == None:     self.subthread = subthread.Subthread()
        else:                 self.subthread = subth
        """

    def run(self, time_heat=10, duty=30, duty_calibrate=8, percent=5):
        #self.subthread.phase = 1

        print("heat start")
        #self.nicrom.heat(t=time_heat)
        #self.nicrom.end()
        print("end")

        #self.subthread.record(comment="open")


        #前進
        print("forward")
        self.motor.forward(duty, duty, 0.05, tick_dutymax=5)
        time.sleep(6)
        self.motor.changeduty(0, 0)
        print("stop")
        time.sleep(1)
        # この時点で地磁気データが使えないので，スタック検知が難しいのが課題
        print("calibration start")
        self.calibrate(duty_calibrate, p=percent)
        print("end")

        #self.subthread.record(comment="deployment")
        print("deployment phase finish")

    def percentpick(self, listdata, p):
        n = int(len(listdata) *p/100)
        listdata = sorted(listdata) # 昇順
        min = listdata[n-1]
        max = listdata[len(listdata)-n]
        return max, min

    def calibrate(self, duty=8, p=5):
        self.mag_list = []
        time_all = 60
        duration = 0.5

        t = 0
        mag_list = []
        self.motor.changeduty(duty, -duty)
        while t <= time_all:
            try:
                self.geomag.get()
                mag_list.append((self.motor.geomag.x, self.motor.geomag.y, self.motor.geomag.z))
                print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(self.geomag.x, self.geomag.y, self.geomag.z) + f"t:{t}")
                print('')
            except:
                print("error") 
            time.sleep(duration)
            t+=duration

        self.motor.changeduty(0,0)
        time.sleep(1)

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

        self.geomag.rads = [(self.maxs[i] - self.mins[i])/2 for i in range(3)]
        self.geomag.aves = [(self.maxs[i] + self.mins[i])/2 for i in range(3)]

        self.geomag.calibrated = True

        with open('lsm303.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(self.maglist)
        with open('calibration_lsm303.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["x, y, z"])
            writer.writerows([self.motor.geomag.rads, self.motor.geomag.aves])

def main():
    deploy_phase = Deploy()
    deploy_phase.run()

if __name__=="__main__":
    main()
