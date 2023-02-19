from class_motor import Motor
import time
import datetime
import csv
import class_geomag

def percentpick(listdata, p):
        n = int(len(listdata) *p/100)
        listdata = sorted(listdata) # 昇順
        min = listdata[n-1]
        max = listdata[len(listdata)-n]
        return max, min

motor = Motor()

duty = 8
p = 5
time_all = 60
duration = 0.5

t = 0
mag_list = []
motor.changeduty(duty, -duty)
while t <= time_all:
    try:
        motor.geomag.get()
        mag_list.append((motor.geomag.x, motor.geomag.y, motor.geomag.z))
        print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(motor.geomag.x, motor.geomag.y, motor.geomag.z) + f"t:{t}")
        print('')
    except:
         print("error") 
    time.sleep(duration)
    t+=duration

motor.changeduty(0,0)
motor.end()

magxs = [mag_list[i][0] for i in range(len(mag_list))]
magys = [mag_list[i][1] for i in range(len(mag_list))]
magzs = [mag_list[i][2] for i in range(len(mag_list))]

# csv save
DIFF_JST_FROM_UTC = 9
jp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
recordname = 'mag/mag_' + str(jp_time).replace(' ', '_').replace(':', '-').replace('.', '_') + '.csv'
with open(recordname, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["magx", "magy", "magz"])
    writer.writerows(mag_list)

# 最大値，最小値の算出
Xmax, Xmin = percentpick(magxs, p)
Ymax, Ymin = percentpick(magys, p)
Zmax, Zmin = percentpick(magzs, p)

maxs = [Xmax, Ymax, Zmax]
mins = [Xmin, Ymin, Zmin]

motor.geomag.rads = [(maxs[i] - mins[i])/2 for i in range(3)]
motor.geomag.aves = [(maxs[i] + mins[i])/2 for i in range(3)]

motor.geomag.calibrated = True

print(f"rads:{motor.geomag.rads}")
print(f"aves:{motor.geomag.aves}")

if(1):
    mag = class_geomag.GeoMagnetic(True, motor.geomag.rads, motor.geomag.aves)
    maglist = []
    while True:
        try:
            mag.get()
            maglist.append([mag.x, mag.y, mag.z])
            print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(mag.x, mag.y, mag.z))
            print(mag.theta_absolute)
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
    with open('lsm303.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(maglist)