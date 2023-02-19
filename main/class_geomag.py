# 地磁気センサーLSM303DLHのクラス用ファイル
import time
import board
import adafruit_lsm303dlh_mag
import csv
import datetime
import math

def percentpick(listdata, p):
    n = int(len(listdata) *p/100)
    listdata = sorted(listdata) # 昇順
    min = listdata[n-1]
    max = listdata[len(listdata)-n]
    return max, min

class GeoMagnetic:
    
    def __init__(self, calibrated=False, rads=[1.0, 1.0, 1.0], aves=[0.0, 0.0, 0.0]):
        self.theta=-1
        self.theta_absolute=-1
        self.i2c = board.I2C()  # uses board.SCL and board.SDA
        self.sensor = adafruit_lsm303dlh_mag.LSM303DLH_Mag(self.i2c)

        self.x, self.y, self.z = [0.0, 0.0, 0.0]
        self.maglist = []
        self.calibrated = calibrated
        self.rads = rads
        self.aves = aves
    
    def get(self):
        self.x, self.y, self.z = self.sensor.magnetic
        self.theta = math.atan2(-self.z, self.x)*180/math.pi
        if self.calibrated:
            self.normalize()
            self.theta_absolute = math.atan2(-self.z, self.x)*180/math.pi
    
    def normalize(self):
        self.x = (self.x - self.aves[0]) / self.rads[0]
        self.y = (self.y - self.aves[1]) / self.rads[1]
        self.z = (self.z - self.aves[2]) / self.rads[2]
    
    def addlist(self):#キャリブレーション用にデータをためる
        self.maglist.append(self.sensor.magnetic)
    
    def calibrate(self):
        t = 0
        duration = 0.5
        while t <= 60:
            self.get()
            self.addlist()
            print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(self.x, self.y, self.z) + f"t:{t}")
            print('')
            t += duration
            time.sleep(duration)
        magxs = [self.maglist[i][0] for i in range(len(self.maglist))]
        magys = [self.maglist[i][1] for i in range(len(self.maglist))]
        magzs = [self.maglist[i][2] for i in range(len(self.maglist))]

        # csv save
        DIFF_JST_FROM_UTC = 9
        jp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
        self.recordname = 'mag/mag_' + str(jp_time).replace(' ', '_').replace(':', '-').replace('.', '_') + '.csv'
        with open(self.recordname, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["magx", "magy", "magz"])
            writer.writerows(self.mag_list)
            
        # 最大値，最小値の算出
        p = 5 # 上位何%をpickするか
        Xmax, Xmin = percentpick(magxs, 5)
        Ymax, Ymin = percentpick(magys, 5)
        Zmax, Zmin = percentpick(magzs, 5)

        self.maxs = [Xmax, Ymax, Zmax]
        self.mins = [Xmin, Ymin, Zmin]
        
        self.rads = [(self.maxs[i] - self.mins[i])/2 for i in range(3)]
        self.aves = [(self.maxs[i] + self.mins[i])/2 for i in range(3)]
        
        self.calibrated = True

def main():
    # mag = GeoMagnetic()
    mag = GeoMagnetic(calibrated=True, rads=[1.45, 1.06, 1.32],aves=[-1.16, -1, 3.15])

    maglist = []
    while True:
        try:
            mag.get()
            maglist.append([mag.x, mag.y, mag.z])
            print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(mag.x, mag.y, mag.z))
            print(mag.theta_absolute)
            time.sleep(1)
        except KeyboardInterrupt:
            break
    with open('lsm303.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(maglist)
    # t = 0
    # duration = 0.5
    # while t <= 5:
    #     t += duration
    #     time.sleep(duration)
    
    # try:
    #     t = 0
    #     while t <= 60:
    #         mag.addlist()
    #         mag.get()
    #         maglist.append([mag.x, mag.y, mag.z])
    #         print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(mag.x, mag.y, mag.z))
    #         print('')
    #         t += duration
    #         time.sleep(duration)
    #     with open('lsm303.csv', 'w') as f:
    #         writer = csv.writer(f)
    #         writer.writerows(maglist)

    # except KeyboardInterrupt:
    #     with open('lsm303.csv', 'w') as f:
    #         writer = csv.writer(f)
    #         writer.writerows(maglist)

if __name__ == "__main__":
    main()
    pass
