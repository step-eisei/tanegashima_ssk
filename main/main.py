# main code in tanegashima 2023!

# class import
import class_pressure
import class_nicrom
import class_motor
import class_distance
import class_gps
import class_geomag
import class_yolo
# phase import
import phase_land
import phase_deployment
import phase_gps
import phase_camera
import phase_distance
# others
import subthread

def main():
    # class define
    pressure = class_pressure.Pressure()
    nicrom = class_nicrom.Nicrom(pin=21)
    geomag = class_geomag.GeoMagnetic()
    motor = class_motor.Motor(geomag=geomag)
    distance = class_distance.Distance()
    gps = class_gps.Gps()
    yolo = class_yolo.CornDetect()
    # phase define
    subth = subthread.Subthread(pressure=pressure, gps=gps, distance=distance, motor=motor)
    land = phase_land.Land(sky=0.1, land=0.01, get_pressure=pressure, subth=subth)
    deployment = phase_deployment.Deploy(motor=motor, nicrom=nicrom, dist_sens=distance, subth=subth)
    gps_phase = phase_gps.Gps_phase(motor, gps, subth)
    camera = phase_camera.Phase_camera(motor=motor, yolo=yolo, distance=distance, subth=subth)
    distance_phase = phase_distance.Distance_phase(distance=distance, motor=motor, subth=subth)
    # main code
    try:
        goal = False
        land.run()
        deployment.run()
        while True:
            gps_phase.run()
            return_camera = camera.run()
            if(return_camera == 0):
                return_distance = distance_phase.run()
                if(return_distance == 0): goal = True
                elif(return_distance == -1): print("goto camera phase.")
                else: print("distance return error.")
            elif(return_camera == -1): print("goto gps phase from camera.")
            else: print("camera return error.")
            if(goal): break
        print("goal judge.")
        motor.end()
        print("GPIO closed.")
        print("enjoy!")
    except KeyboardInterrupt:
        print("\nInterrupted.")
        motor.end()
        print("GPIO closed.")
        print("not enjoy.")

if __name__ == "__main__":
    main()
