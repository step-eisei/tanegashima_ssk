import sys
sys.path.append("/home/pi/tanegashima_ssk/main/yolov7/")
from yolov7 import class_yolo
import class_motor
import class_distance
import class_geomag
#import subthread
import time
import math

class Phase_camera:
    def __init__(self, motor=None, yolo=None, distance=None): #, subthread=subthread.Subthread()):
        if yolo == None:
            self.yolo = class_yolo.CornDetect()
        else:
            self.yolo = yolo
        if motor == None:
            self.motor = class_motor.Motor()
        else:
            self.motor = motor
        if distance == None:
            self.distance = class_distance.Distance()
        else:
            self.distance = distance
        self.motor.geomag.calibrated = True
        #self.subthread = subthread

        # const
        self.forward_time = 5
        self.angle_thres = 10
        self.image_size = [640, 480]
  
    # calculate angle from photo
    def calc_angle(self, c1, c2):
        if c1 == [-1, -1]:
            return 180
        x1, x2 = c1[0], c2[0]

        x_med = (x1 + x2) / 2
        x_dist = -2 * (x_med - self.image_size[0] / 2) / self.image_size[0]   #-1~1 中央からx方向にどれくらい離れてるか -1~1
        print(f"x_dist:{x_dist}")
        """
        cone_width = (x1-x2) / self.image_size[0] #コーンの横幅が画像の幅を占める割合
        z_const = 1                               #コーンまでの距離を推定するのに調整する定数
        z_dist = z_const * (1 / cone_width) - 1   #コーンの幅からコーンまでの距離を推定

        angle = math.degrees(math.atan2(x_dist, z_dist))
        """

        c = 1 #調整用の定数
        angle = math.degrees(math.atan(c * x_dist))
        print(f"angle:{angle}")
        return angle
    
    # check distance between body and red cone
    def check_distance(self):
        self.distance.reading()

        return self.distance.distance
 

    def forward(self): 
        self.motor.forward(30, 30, time_sleep=0.05, tick_dutymax=5)
        time.sleep(self.forward_time)
        self.motor.forward(5, 5, 0.05, tick_dutymax=5)
        self.motor.changeduty(0,0)
    
    
    def run(self):
        #self.subthread.phase = 3
        i = 0

        while True:
            # take a photo and image-processing
            print("take photo")
            c1, c2 = self.yolo.image_process()
            print(c1, c2)

            if abs(self.calc_angle(c1, c2)) <= self.angle_thres:  # red cone in the center of image
                print("cone is in the centre")
                i = 0
                dist = self.check_distance()
                print(f"dist:{dist}")
                if dist <= 1:  # distance of red cone is 1m
                    # goto phase_distance
                    print("goto phase_distance")
                    return 0
                            
                else:
                    self.forward()

            else:  # red cone not in the center of image
                if c1 != [-1, -1] and c2 != [-1, -1]: # red cone in image
                    print("cone is detected")
                    i = 0
                    angle = self.calc_angle(c1, c2)
                    self.motor.rotate(angle)
                
                else:  # red cone not in image
                    print("cone is NOT in the image")
                    if i < 12: 
                        i += 1
                        self.motor.rotate(30)
                    
                    else:  # back to phase_GPS
                        self.forward()

                        print("back to phase_gps")
                        #return -1
    
    
def main():
    phase_camera = Phase_camera()
    phase_camera.run()
    
if __name__ == "__main__":
    main()
