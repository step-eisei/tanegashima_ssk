
import time
import numpy as np
import math
import class_motor
import class_gps
import class_geomag
import subthread

class Gps_phase():
    def __init__(self, motor=class_motor.Motor(), gps=class_gps.Gps(), mag=class_geomag.GeoMagnetic(), subthread=subthread.Subthread()):
        # goal座標取得プログラムより取得
        self.goal_lati = -1
        self.goal_longi = -1
        self.duty_constant=0.5
        self.motor = motor
        self.gps = gps
        self.mag = mag
        self.subthread = subthread
        self.x, self.y = self.calc_xy(self.gps.latitude, self.gps.longitude, self.goal_lati, self.goal_longi)

    def run(self, duty_R_max=50, duty_L_max=50):
        first = True
        duty_R = duty_R_max
        duty_L = duty_L_max
        while True:
            lati = self.gps.latitude
            longi = self.gps.longitude
            x0, y0 = (self.x, self.y)#前回位置
            theta_relative0 = theta_relative
            self.x, self.y = self.calc_xy(lati, longi, self.goal_lati, self.goal_longi)#ゴールを中心とした現在位置
            distance = math.sqrt(self.x**2+self.y**2)
            if(distance<3): return 0

            moved = math.sqrt((self.x - x0) ** 2 + (self.y - y0) ** 2)#前ループからどれくらい動いたか
            if not(first) and moved <= 0.03:
                self.motor.changeduty(0, 0)
                self.mag.get()
                theta_past = self.mag.theta_absolute
                self.motor.rotate(90, threshold_angle=90)
                self.mag.get()
                theta_now = self.mag.theta_absolute
                if (self.motor.angle_difference(theta_past, theta_now)<30): self.motor.stack() #動いてなければスタック処理
                first = True
            else:
                self.mag.get()
                theta_absolute = self.mag.theta_absolute#地磁気から得た角度
                theta_relative = self.angle(self.x, self.y, theta_absolute) #ゴールと比べた時の角度
                if(first):
                    self.motor.forward(duty_R, duty_L, 0.05, tick_dutymax=5)
                else:
                    if(distance < moved):
                        duty_R_max = int(duty_R_max*distance/moved)
                        duty_L_max = int(duty_L_max*distance/moved)
#課題
                    self.motor.changeduty(30-theta_relative/6, 30+theta_relative/6)#モーターのDuty比を変更
                time.sleep(1)#1秒走る
                first = False
    
    # ゴール角度，機体の角度から機体の回転角度を求める関数
    def angle(self, x_now, y_now, theta_absolute):
        # ゴール角度算出
        theta_gps = math.atan2(y_now, x_now) * 180/math.pi
        # 機体正面を0として，左を正，右を負とした変数(-180~180)を作成
        theta_relative = theta_gps + theta_absolute + 90
        if(theta_relative > 180): theta_relative -= 360
        if(theta_relative < -180): theta_relative += 360
        return theta_relative

    # gpsからゴール基準で自己位置を求める関数(国土地理院より)
    def calc_xy(self, gps_latitude, gps_longitude, goal_latitude, goal_longitude):
        
        """ 緯度経度を平面直角座標に変換する
        - input:
            (gps_latitude, gps_longitude): 変換したい緯度・経度[度]（分・秒でなく小数であることに注意）
            (goal_latitude, goal_longitude): 平面直角座標系原点の緯度・経度[度]（分・秒でなく小数であることに注意）
        - output:
            x: 変換後の平面直角座標[m]
            y: 変換後の平面直角座標[m]
        """
        # 緯度経度・平面直角座標系原点をラジアンに直す
        phi_rad = np.deg2rad(gps_latitude)
        lambda_rad = np.deg2rad(gps_longitude)
        phi0_rad = np.deg2rad(goal_latitude)
        lambda0_rad = np.deg2rad(goal_longitude)

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
        return (Y, X) # [m]，(x_now, y_now)で，軸が反転している．

def main():
    gps_phase = Gps_phase()
    gps_phase.run()

if __name__=="__main__":
    main()
