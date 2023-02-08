# 地磁気センサーLSM303DLHのクラス用ファイル
import time
import board
import adafruit_lsm303dlh_mag
import csv
import sys
import math

# def percentpick(listdata, p):
#     n = int(len(listdata) *p/100)
#     listdata = sorted(listdata) # 昇順
#     min = listdata[n-1]
#     max = listdata[len(listdata)-n]
#     return max, min

class GeoMagnetic:
    
    def __init__(self, calibrated=False, rads=[1.0, 1.0, 1.0], aves=[0.0, 0.0, 0.0]):
        self.theta=-1
        self.theta_absolute=-1
        self.i2c = board.I2C()  # uses board.SCL and board.SDA
        self.sensor = adafruit_lsm303dlh_mag.LSM303DLH_Mag(self.i2c)

        self.x, self.y, self.z = [0.0, 0.0, 0.0]
        #self.maglist = []
        self.calibrated = calibrated
        self.rads = rads
        self.aves = aves
    
    def get(self):
        self.x, self.y, self.z = self.sensor.magnetic
        self.theta = math.atan2(self.y, self.x)*180/math.pi
        if self.calibrated:
            self.normalize()
            self.theta_absolute = math.atan2(self.y, self.x)*180/math.pi
    
    def normalize(self):
        #rads = [self.maxs[i] - self.mins[i] for i in range(3)]
        #aves = [self.maxs[i] + self.mins[i] for i in range(3)]
        
        self.x = (self.x - self.aves[0]) / self.rads[0]
        self.y = (self.y - self.aves[1]) / self.rads[1]
        self.z = (self.z - self.aves[2]) / self.rads[2]
    
#     def addlist(self):#キャリブレーション用にデータをためる
#         self.maglist.append(self.sensor.magnetic)
    
#     def calibrate(self):
#         magxs = [self.maglist[i][0] for i in range(len(self.maglist))]
#         magys = [self.maglist[i][1] for i in range(len(self.maglist))]
#         magzs = [self.maglist[i][2] for i in range(len(self.maglist))]

#         # 最大値，最小値の算出
#         p = 5 # 上位何%をpickするか
#         Xmax, Xmin = percentpick(magxs)
#         Ymax, Ymin = percentpick(magys)
#         Zmax, Zmin = percentpick(magzs)

#         self.maxs = [Xmax, Ymax, Zmax]
#         self.mins = [Xmin, Ymin, Zmin]

#         self.calibrated = True

def main():
    mag = GeoMagnetic()

    t = 0
    duration = 0.5
    maglist = []
    while t <= 5:
        t += duration
        time.sleep(duration)
    
    try:
        t = 0
        while t <= 60:
            #mag.addlist()
            mag.get()
            maglist.append([mag.x, mag.y, mag.z])
            print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(mag.x, mag.y, mag.z))
            print('')
            t += duration
            time.sleep(duration)
        with open('lsm303.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(maglist)

    except KeyboardInterrupt:
        with open('lsm303.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(maglist)

if __name__ == "__main__":
    main()
    pass
