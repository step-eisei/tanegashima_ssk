# カメラフェーズ

import class_yolo
import class_geomag
import class_gps
import class_motor
import class_distance
import phase_deployment
import time

class Phase_camera:
    def __init__(self, yolo, geomag, gps, motor):
        pass
    
    # calculate angle from photo
    def calc_angle(self):
        pass
    
    # check red cone in photo
    def check_cone(self):
        pass
    
    # rotate body
    def rotate(self):
        pass
    
    # check distance between body and red cone
    def check_distance(self):
        pass
    
    def run(self):
         i = 0
    bool_mag = True
    bool_takephoto = True
    bool_redcone = True
    while(bool_mag):
        # get geomag
        geomag.get()
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
                            --
                            bool_takephoto = False
                            bool_redcone = False
                    else: pass
                else:
                    if(i<12):
                        #rotate 30 deg.
                        deployment.rotate(30)
                        i += 1
                        bool_redcone = False
                    else:
                        # forward n sec.
                        forward_time = n
                        # set duty
                        duty = 60
                        print("forward start for" + str(forward_time)+ "seconds")
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
