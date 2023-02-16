# カメラフェーズ

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
    def __init__(self, yolo=class_yolo.CornDetect(), geomag=class_geomag.GeoMagnetic(), gps=class_gps.Gps(), motor=class_motor.Motor(), distance=class_distance.Distance(), subthread=subthread.Subthread()):
        self.yolo = yolo
        self.geomag = geomag
        self.gps = gps
        self.motor = motor
        self.distance = distance
        self.subthread = subthread
        pass
    
    # calculate angle from photo
    def calc_angle(self, c1, c2):
        image_size = [1920, 1080]

        x1, x2 = c1[0], c2[0]
        cone_width = (x1-x2) / image_size[0]   #コーンの横幅が画像の幅を占める割合
        z_const = 1                            #コーンまでの距離を推定するのに調整する定数
        z_dist = z_const * (1 / cone_width) - 1#コーンの幅からコーンまでの距離を推定

        x_med = (x1 + x2) / 2
        x_dist = x_med - image_size[0] / 2   #中央からx方向にどれくらい離れてるか

        angle = math.atan2(z_dist, x_dist)

        return angle
    
    # check red cone in photo
    def check_cone(self):
        c1, c2 = self.yolo.estimate

        if c1 == [-1, -1] and c2 == [-1, -1]:
            return False
        else:
            return True
    
    # rotate body
    #def rotate(self, ang):
    #    self.motor.rotate(angle=ang)
    
    # check distance between body and red cone
    def check_distance(self):
        self.distance.reading

        return self.distance.distance
    
    def run(self):
        self.subthread.phase = 3
        i = 0
        bool_mag = True
        bool_takephoto = True
        bool_redcone = True
        while(bool_mag):
            # get geomag
            self.geomag.get()
            while(bool_takephoto):
                # take a photo
                --
                # image-processing
                --

                while(bool_redcone):
                    if(0):# red cone in photo
                        # rotate to red cone
                        --
                        # take a photo
                        --
                        # image-processing
                        --
                        if(0):# red cone in the center of image
                            if(0):# distance of red cone is 1m
                                # goto phase_distance
                                return 0
                                pass
                            else:
                                # forward n sec.
                                forward_time = n
                                # set duty
                                duty = 60
                                print("forward for" + str(forward_time)+ "seconds")
                                for i in range(10):
                                    duty_new = int(duty/10*(i+1))
                                    motor.changeduty(duty_new, duty_new)
                                    time.sleep(forward_time/10)
                                
                                bool_takephoto = False
                                bool_redcone = False
                        else: pass
                    else:
                        if(i<12):
                            #rotate 30 deg.
                            self.motor.rotate(30)
                            i += 1
                            bool_redcone = False
                        else:
                            # forward n sec.
                            forward_time = n
                            # set duty
                            duty = 60
                            print("forward for" + str(forward_time)+ "seconds")
                            for i in range(10):
                                duty_new = int(duty/10*(i+1))
                                motor.changeduty(duty_new, duty_new)
                                time.sleep(forward_time/10)

                            # get gps
                            if(0):# distance of red cone is over3m
                                # goto gps
                                return -1
                                pass
                            else: bool_redcone = False
        
    
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
