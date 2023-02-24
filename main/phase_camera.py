import sys
sys.path.append("/home/pi/tanegashima_ssk/main/yolov7/")
import class_yolo
import class_motor
import class_distance
#import subthread
import time
import math
import cv2

class Phase_camera:
    def __init__(self, motor=None, yolo=None, distance=None): #, subthread=None):
        if yolo == None:     self.yolo = class_yolo.CornDetect()
        else:                self.yolo = yolo

        if motor == None:     self.motor = class_motor.Motor()
        else:                 self.motor = motor
        self.motor.geomag.calibrated = True
        self.geomag = self.motor.geomag

        if distance == None:  self.distance = class_distance.Distance()
        else:                 self.distance = distance

        """
        if subthread == None: self.subthread = subthread.Subthread()
        else:                 self.subthread = subthread
        """
        # const
        self.angle_thres = 10
        self.image_size = [640, 480]
  
    # calculate angle from photo
    def calc_angle(self, c1, c2):
        if c1 == [-1, -1]:
            return 180
        x1, x2 = c1[0], c2[0] #コーンの左と右のx座標

        x_med = (x1 + x2) / 2 #コーンの中央が画像のどの位置にいるか
        x_dist = -2 * (x_med - self.image_size[0] / 2) / self.image_size[0]   #中央からx方向にどれくらい離れてるか -1~1まで取る
        print(f"x_dist:{x_dist}")
        """
        cone_width = (x1-x2) / self.image_size[0] #コーンの横幅が画像の幅を占める割合
        z_const = 1                               #コーンまでの距離を推定するのに調整する定数
        z_dist = z_const * (1 / cone_width) - 1   #コーンの幅からコーンまでの距離を推定

        angle = math.degrees(math.atan2(x_dist, z_dist))
        """

        c = 1 #調整用の定数
        angle = math.degrees(math.atan(c * x_dist)) #コーンに向くまでの角度を計算 c=1の場合 -45~45度
        print(f"angle:{angle}")
        return angle
    
    # check distance between body and red cone
    def check_distance(self):
        self.distance.reading()

        return self.distance.distance
    
    def angle_difference(self, from_angle, to_angle):
        angle = to_angle-from_angle
        if(angle<-180): return angle+360
        elif(angle>180): return angle-360
        return angle
    
    def forward(self, forward_time): 
        self.geomag.get()
        angle_before = self.geomag.theta_absolute

        self.motor.forward(30, 30, time_sleep=0.05, tick_dutymax=5)
        time.sleep(forward_time)
        self.motor.forward(10, 10, 0.1, tick_dutymax=5)
        self.motor.changeduty(0,0)
        time.sleep(1)

        self.geomag.get()
        angle_after = self.geomag.theta_absolute
        angle_diff = self.angle_difference(angle_before, angle_after)
        print(angle_diff)
        c = 10
        if angle_diff > 0:
            angle_diff += forward_time * c
        elif angle_diff < 0:
            angle_diff -= forward_time * c
        angle_diff += 10

        print(-angle_diff)
        self.motor.rotate(-angle_diff)
    
    
    def run(self):
        #self.subthread.phase = 3
        i = 0 #コーンが見つからずその場で回転した回数
        j = 0 #写真の番号

        while True:
            dist = self.check_distance() #距離を測る
            print(f"dist:{dist}")

            if 20 <= dist <= 50:  # distance of red cone is within 50cm
                # goto phase_distance
                print("goto phase_distance")
                return 0
            
            # take a photo and image-processing
            print("take photo")
            c1, c2, image = self.yolo.image_process()
            j+=1
            cv2.imwrite(f"camera/image{j}.jpg", image)
            print(c1, c2) #print the coordinates of the cone

            if abs(self.calc_angle(c1, c2)) <= self.angle_thres:  # red cone in the center of image
                print("cone is in the centre")
                print("forward")
                i = 0
                forward_time = min(200/(c2[0] - c1[0]), 3)
                self.forward(forward_time)

            else:  # red cone is NOT in the center of image
                if c1 != [-1, -1] and c2 != [-1, -1]: # red cone is in the image
                    print("cone is detected")
                    i = 0
                    angle = self.calc_angle(c1, c2)
                    self.motor.rotate(angle)
                
                else:  # red cone is NOT in the image
                    print("cone is NOT in the image")

                    if 50 < dist < 100: # コーンがカメラで見つからなくても、距離センサが反応すれば前進する
                        i = 0
                        print("cone is near")
                        print("forward")
                        self.motor.forward(15, 15, 0.05, tick_dutymax=5)#距離に応じて前進
                        time.sleep(dist/30)
                        self.motor.changeduty(0,0)

                    elif i < 12: #その場で回転
                        i += 1
                        self.motor.rotate(30)
                    
                    else:  # back to phase_GPS
                        self.forward()

                        print("back to phase_gps")
                        return -1
    
    
def main():
    phase_camera = Phase_camera()
    phase_camera.run()
    
if __name__ == "__main__":
    main()
