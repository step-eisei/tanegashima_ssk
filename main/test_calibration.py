from class_motor import Motor
import time

def percentpick(listdata, p):
        n = int(len(listdata) *p/100)
        listdata = sorted(listdata) # 昇順
        min = listdata[n-1]
        max = listdata[len(listdata)-n]
        return max, min

motor = Motor()

duty = 10
p = 5
mag_list = []

t = 0
duration = 1

motor.changeduty(duty, -duty)
while t <= 60:
    motor.geomag.get()
    mag_list.append((motor.geomag.x, motor.geomag.y, motor.geomag.z))
    print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(motor.geomag.x, motor.geomag.y, motor.geomag.z) + f"t:{t}")
    print('')
    time.sleep(duration)
    t+=duration

motor.changeduty(0,0)
motor.end()

magxs = [mag_list[i][0] for i in range(len(mag_list))]
magys = [mag_list[i][1] for i in range(len(mag_list))]
magzs = [mag_list[i][2] for i in range(len(mag_list))]

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