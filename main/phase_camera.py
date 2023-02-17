import sys
sys.path.append("/home/pi/tanegashima_ssk/main/yolo/")
from yolo import class_yolo
import class_motor
import class_distance
import subthread
import time
import math

class Phase_camera:
    def __init__(self, yolo=class_yolo.Yolo(), motor=class_motor.Motor(), distance=class_distance.Distance(), subthread=subthread.Subthread()):
        self.yolo = yolo
        self.motor = motor
        self.distance = distance
        self.subthread = subthread

        # const
        self.forward_time = 5
        self.angle_thres = 10
        self.image_size = [640, 480]
        pass
    
  
    # calculate angle from photo
    def calc_angle(self, c1, c2):
        if c1 == [-1, -1]:
            return 180
        x1, x2 = c1[0], c2[0]

        x_med = (x1 + x2) / 2
        x_dist = 2 * (x_med - self.image_size[0] / 2) / self.image_size[0]   #-1~1 中央からx方向にどれくらい離れてるか -1~1

        """
        cone_width = (x1-x2) / self.image_size[0] #コーンの横幅が画像の幅を占める割合
        z_const = 1                               #コーンまでの距離を推定するのに調整する定数
        z_dist = z_const * (1 / cone_width) - 1   #コーンの幅からコーンまでの距離を推定

        angle = math.degrees(math.atan2(x_dist, z_dist))
        """

        c = 3 #調整用の定数
        angle = math.degrees(math.atan(c * x_dist))

        return angle
    
    # check distance between body and red cone
    def check_distance(self):
        self.distance.reading

        return self.distance.distance
 
    
    def forward_for_n(self, n): 
        # forward n sec.
        forward_time = n
        # set duty
        duty = 60
        print("forward for" + str(forward_time)+ "seconds")
        for i in range(10):
            duty_new = int(duty/10*(i+1))
            self.motor.changeduty(duty_new, duty_new)
            time.sleep(forward_time/10/2)
        for i in range(10):
            duty_new = int(duty/10*(10-i-1))
            self.motor.changeduty(duty_new, duty_new)
            time.sleep(forward_time/10/2)

        self.motor.changeduty(0,0)

    def run(self):
        self.subthread.phase = 3
        i = 0

        while True:
            # take a photo and image-processing
            print("take photo")
            c1, c2 = self.yolo.image_process()
            print(c1, c2)

            if abs(self.calc_angle(c1, c2)) <= self.angle_thres:  # red cone in the center of image
                print("cone is in the centre")
                i = 0
                if self.check_distance <= 1:  # distance of red cone is 1m
                    # goto phase_distance
                    print("goto phase_distance")
                    return 0
                            
                else:
                    self.forward_for_n(self.forward_time)

            else:  # red cone not in the center of image
                if c1 != [-1, -1] and c2 != [-1, -1]: # red cone in image
                    print("cone is detected")
                    i = 0
                    self.motor.rotate(self.calc_angle(c1, c2))
                
                else:  # red cone not in image
                    print("cone is NOT in the image")
                    if i < 12: 
                        i += 1
                        self.motor.rotate(30)
                    
                    else:  # back to phase_GPS
                        self.forward_for_n(self.forward_time)

                        print("back to phase_gps")
                        return -1
    
    
def main():
    Phase_camera = Phase_camera()
    Phase_camera.run()
    
if __name__ == "__main__":
    main()
