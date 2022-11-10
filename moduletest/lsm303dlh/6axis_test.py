# i2c通信，1 secごとに地磁気データを出力する関数
import time
import board
import adafruit_lsm303dlh_mag
import csv

i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)

t = 0
duration = 0.5
maglist = []
while t <= 60:
    mag_x, mag_y, mag_z = sensor.magnetic
    maglist.append([mag_x,mag_y,mag_z])
    print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(mag_x, mag_y, mag_z))
    print('')
    
    t += duration
    time.sleep(duration)
    
with open('lsm303.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(maglist)
