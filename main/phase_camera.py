import class_yolo
import class_geomag
import class_gps
import class_motor
import class_distance
import phase_deployment
import subthread
import time
import math

class Phase_camera:
    def __init__(self, yolo=class_yolo.Yolo(), geomag=class_geomag.GeoMagnetic(), gps=class_gps.Gps(), motor=class_motor.Motor(), distance=class_distance.Distance(), subthread=subthread.Subthread()):
        self.yolo = yolo
        self.geomag = geomag
        self.gps = gps
        self.motor = motor
        self.distance = distance
        self.subthread = subthread

        # const
        self.forward_time = 5
        self.angle_thres = 10
        self.image_size = [1920, 1080]
        pass
    
  
    # calculate angle from photo
    def calc_angle(self, c1, c2):
        x1, x2 = c1[0], c2[0]
        cone_width = (x1-x2) / self.image_size[0]   #コーンの横幅が画像の幅を占める割合
        z_const = 1                            #コーンまでの距離を推定するのに調整する定数
        z_dist = z_const * (1 / cone_width) - 1#コーンの幅からコーンまでの距離を推定

        x_med = (x1 + x2) / 2
        x_dist = x_med - self.image_size[0] / 2   #中央からx方向にどれくらい離れてるか

        angle = math.atan2(z_dist, x_dist)

        return angle
    
    # check red cone in photo
    def check_cone(self):
        c1, c2 = self.yolo.estimate

        if c1 == [-1, -1] and c2 == [-1, -1]:
            return False
        else:
            return True
    
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
            time.sleep(forward_time/10)

    def run(self):
        self.subthread.phase = 3
        i = 0

        while True:
            # take a photo and image-processing
            c1, c2 = self.yolo.image_process()

            if abs(self.calc_angle(c1, c2)) <= self.angle_thres:  # red cone in the center of image
                if self.check_distance <= 1:  # distance of red cone is 1m
                    # goto phase_distance
                    return 0
                            
                else:
                    self.forward_for_n(self.forward_time)

            else:  # red cone not in the center of image
                if c1 != [-1, -1] and c2 != [-1, -1]: # red cone in image
                    self.motor.rotate(self.calc_angle(c1, c2))
                
                else:  # red cone not in image
                    if i < 12: 
                        i += 1
                        self.motor.rotate(30)
                    
                    else:  # back to phase_GPS
                        self.forward_for_n(self.forward_time)
                        return -1
    
    
def main():
    yolo = class_yolo
    geomag = class_geomag
    gps = class_gps
    motor = class_motor
    deployment = phase_deployment
    Phase_camera = Phase_camera(yolo, geomag, gps, motor)
    Phase_camera.run()
    
if __name__ == "__main__":
    main()
