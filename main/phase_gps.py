
import time
import numpy as np
import math
import class_motor
import class_gps
import class_geomag
# import subthread
import csv
import datetime

class Gps_phase():
    def __init__(self, motor=class_motor.Motor(), gps=class_gps.Gps(), mag=class_geomag.GeoMagnetic(), subthrea=None):
#         if(subthrea==None): subthrea = subthread.Subthread(geomag=mag, gps=gps, motor=motor)
        DIFF_JST_FROM_UTC = 9
        jp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
        self.gps_name = 'gps/phase_gps' + str(jp_time).replace(' ', '_').replace(':', '-').replace('.', '_') + '.csv'
        with open(self.gps_name, 'w', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["lati", "longi", "g_lati", "g_longi", "x", "y", "distance", "move", "theta_abs", "theta_rela", "theta_delta", "duty", "duty_R", "duty_L"])
        
        with open ('goal.csv', 'r') as f :# goal座標取得プログラムより取得
            reader = csv.reader(f)
            line = [row for row in reader]
            self.goal_lati = float(line[ 1 ] [ 0 ])
            self.goal_longi = float(line[ 1 ] [ 1 ])
        self.duty_constant=0.5
        self.motor = motor
        self.gps = gps
        self.mag = mag
        # self.subthread = subthrea
        self.renew_data()

    def run(self, duty_max=25):
        # self.subthread.phase = 2
        first = True
        duty_R = duty_L = duty_max
        stack = 0
        theta_delta = 1000
        while True:
            x0, y0 = (self.x, self.y)#前回位置
            if(not first): theta_previous = self.theta_relative
            while True:
                self.renew_data()
                if(self.distance<50): break
            if(self.distance<3): # goto camera phase
                with open(self.gps_name, 'a', newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([self.gps.latitude, self.gps.longitude, self.goal_lati, self.goal_longi, self.x, self.y, self.distance, moved, self.mag.theta_absolute, self.theta_relative, theta_delta, duty_max, duty_R, duty_L])
                self.motor.forward(5, 5, 0.05, tick_dutymax=2)
                self.motor.changeduty(0, 0)
                time.sleep(1)
                self.motor.end()
                print("distance < 3")
                # self.subthread.record(comment="gps")
                return 0
            elif(self.distance<7): duty_max = 15
            elif(self.distance<12): duty_max = 20
            moved = math.sqrt((self.x - x0) ** 2 + (self.y - y0) ** 2)#前ループからどれくらい動いたか
            if(moved <= 0.03): stack +=1
            else             : stack = 0
            if(first): self.motor.forward(duty_R, duty_L, 0.05, tick_dutymax=5)
            elif (stack > 9):
                print("stacking?")
                # 動けていない場合
                self.motor.changeduty(0, 0)
                self.renew_data(gps=False)
                theta_previous = self.theta_relative
                self.motor.rotate(90, threshold_angle=90)
                self.renew_data(gps=False)
                if (self.motor.angle_difference(theta_previous, self.theta_relative)<30): self.motor.stack() #動いてなければスタック処理
                first = True
                stack = 0
                # self.subthread.record(comment="notmove")
            else:
                if(abs(duty_R-duty_L)>3): duty_R=duty_L # due to feedback delay
                theta_delta = self.motor.angle_difference(self.theta_relative, theta_previous)
                # Proportional control
                if(abs(self.theta_relative)<60):    duty_delta = 1
                elif(abs(self.theta_relative)<150): duty_delta = 2
                else:                               duty_delta = 3
                # Derivative control
                if(math.floor(abs(self.theta_relative/(3*theta_delta)))<int(duty_max/5)): duty_delta += math.floor(abs(self.theta_relative/(2*theta_delta)))
                else:                                                       duty_delta += int(duty_max/5)
                # adjust duty
                if(self.theta_relative<0):  duty_R -= duty_delta
                else:                       duty_L -= duty_delta
                duty_difference = duty_max-max(duty_R, duty_L)
                duty_R += duty_difference
                duty_L += duty_difference
                self.motor.forward(duty_R, duty_L, time_sleep=0.05, tick_dutymax=5) # motor
                # self.subthread.record(comment="dutychange")
            print("")
            print(f"now  GPS            :{self.gps.latitude, self.gps.longitude}")
            print(f"goal GPS            :{self.goal_lati, self.goal_longi}")
            print(f"previous position   :{x0, y0}")
            print(f"now      position   :{self.x, self.y}")
            print(f"distance, move      :{self.distance, moved}")
            print(f"theta_absolute      :{self.mag.theta_absolute}")
            print(f"theta_relative      :{self.theta_relative}")
            print(f"theta_delta         :{theta_delta}")
            print(f"duty_max            :{duty_max}")
            print(f"duty                :{duty_R, duty_L}")
            with open(self.gps_name, 'a', newline="") as f:
                writer = csv.writer(f)
                writer.writerow([self.gps.latitude, self.gps.longitude, self.goal_lati, self.goal_longi, self.x, self.y, self.distance, moved, self.mag.theta_absolute, self.theta_relative, theta_delta, duty_max, duty_R, duty_L])
            time.sleep(1)#1秒走る
            first = False

    # gps, magを取得して更新するメソッド
    def renew_data(self, gps=True, mag=True):
        if(gps):
            self.calc_xy()
            self.distance = math.sqrt(self.x**2+self.y**2)
        if(mag):
            self.mag.get()
            self.angle()

    # ゴール角度，機体の角度から機体の回転角度を求めるメソッド
    def angle(self):
        # ゴール角度算出
        theta_gps = math.atan2(-self.y, -self.x)*180/math.pi - 90
        if(theta_gps > 180): theta_gps -= 360
        if(theta_gps < -180): theta_gps += 360
        # print(f"theta_goal    :{theta_gps}")
        # 機体正面を0として，左を正，右を負とした変数(-180~180)を作成
        self.theta_relative = self.motor.angle_difference(self.mag.theta_absolute, theta_gps)

    # gpsからゴール基準で自己位置を求める関数(国土地理院より)
    def calc_xy(self):
        
        """ 緯度経度を平面直角座標に変換する
        - input:
            (gps_latitude, gps_longitude): 変換したい緯度・経度[度]（分・秒でなく小数であることに注意）
            (goal_latitude, goal_longitude): 平面直角座標系原点の緯度・経度[度]（分・秒でなく小数であることに注意）
        - output:
            x: 変換後の平面直角座標[m]
            y: 変換後の平面直角座標[m]
        """
        # 緯度経度・平面直角座標系原点をラジアンに直す
        phi_rad = np.deg2rad(self.gps.latitude)
        lambda_rad = np.deg2rad(self.gps.longitude)
        phi0_rad = np.deg2rad(self.goal_lati)
        lambda0_rad = np.deg2rad(self.goal_longi)

        # 補助関数
        def A_array(n):
            A0 = 1 + (n**2)/4. + (n**4)/64.
            A1 = -     (3./2)*( n - (n**3)/8. - (n**5)/64. )
            A2 =     (15./16)*( n**2 - (n**4)/4. )
            A3 = -   (35./48)*( n**3 - (5./16)*(n**5) )
            A4 =   (315./512)*( n**4 )
            A5 = -(693./1280)*( n**5 )
            return np.array([A0, A1, A2, A3, A4, A5])

        def alpha_array(n):
            a0 = np.nan # dummy
            a1 = (1./2)*n - (2./3)*(n**2) + (5./16)*(n**3) + (41./180)*(n**4) - (127./288)*(n**5)
            a2 = (13./48)*(n**2) - (3./5)*(n**3) + (557./1440)*(n**4) + (281./630)*(n**5)
            a3 = (61./240)*(n**3) - (103./140)*(n**4) + (15061./26880)*(n**5)
            a4 = (49561./161280)*(n**4) - (179./168)*(n**5)
            a5 = (34729./80640)*(n**5)
            return np.array([a0, a1, a2, a3, a4, a5])

        # 定数 (a, F: 世界測地系-測地基準系1980（GRS80）楕円体)
        m0 = 0.9999
        a = 6378137.
        F = 298.257222101

        # (1) n, A_i, alpha_iの計算
        n = 1. / (2*F - 1)
        A_array = A_array(n)
        alpha_array = alpha_array(n)

        # (2), S, Aの計算
        A_ = ( (m0*a)/(1.+n) )*A_array[0] # [m]
        S_ = ( (m0*a)/(1.+n) )*( A_array[0]*phi0_rad + np.dot(A_array[1:], np.sin(2*phi0_rad*np.arange(1,6))) ) # [m]

        # ここまで定数．今後はA_，　S_，　alpha_arrayのみを利用
        
        # (3) lambda_c, lambda_sの計算
        lambda_c = np.cos(lambda_rad - lambda0_rad)
        lambda_s = np.sin(lambda_rad - lambda0_rad)

        # (4) t, t_の計算
        t = np.sinh( np.arctanh(np.sin(phi_rad)) - ((2*np.sqrt(n)) / (1+n))*np.arctanh(((2*np.sqrt(n)) / (1+n)) * np.sin(phi_rad)) )
        t_ = np.sqrt(1 + t*t)

        # (5) xi', eta'の計算
        xi2  = np.arctan(t / lambda_c) # [rad]
        eta2 = np.arctanh(lambda_s / t_)

        # (6) x, yの計算
        X = A_ * (xi2 + np.sum(np.multiply(alpha_array[1:],
                                        np.multiply(np.sin(2*xi2*np.arange(1,6)),
                                                    np.cosh(2*eta2*np.arange(1,6)))))) - S_ # [m]
        Y = A_ * (eta2 + np.sum(np.multiply(alpha_array[1:],
                                            np.multiply(np.cos(2*xi2*np.arange(1,6)),
                                                        np.sinh(2*eta2*np.arange(1,6)))))) # [m]
        
        # return
        self.x = Y
        self.y = X # [m]，(x_now, y_now)で，軸が反転している．

def main():
    try:
        with open ('calibration_lsm303.csv', 'r') as f :# goal座標取得プログラムより取得
            reader = csv.reader(f)
            line = [row for row in reader]
            rads = [float(line[1][i]) for i in range(3)]
            aves = [float(line[2][i]) for i in range(3)]
        gps_phase = Gps_phase(mag=class_geomag.GeoMagnetic(True, rads, aves))
        gps_phase.run()
    except KeyboardInterrupt:
        gps_phase.motor.end()
        print("terminated.")

if __name__=="__main__":
    main()
