import class_yolo
import class_geomag
import class_gps
import class_motor
import class_distance
import phase_deployment
import subthread
import time

class Phase_camera:
    def __init__(self, yolo=class_yolo.Yolo(), geomag=class_geomag.GeoMagnetic(), gps=class_gps.Gps(), motor=class_motor.Motor(), distance=class_distance.Distance(), subthread=subthread.Subthread()):
        self.yolo = yolo
        self.geomag = geomag
        self.gps = gps
        self.motor = motor
        self.distance = distance
        self.subthread = subthread

        # const
        self.forward_time = n
        self.angle_thres = 10
        pass
    
    # calculate angle from photo
    def calc_angle(self, c1, c2):
        pass
    
    # check red cone in photo
    def check_cone(self):
        pass
    
    # check distance between body and red cone
    def check_distance(self):
        pass
    
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
