# main code in tanegashima 2023!

# サブスレッド処理未完了
# ピン番号等の変数未完了

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
    geomag = class_geomag.GeoMagnetic(calibrated=False)
    motor = class_motor.Motor(200, 5, 6, 19, 26, geomag=geomag)
    distance = class_distance.Distance(9, 11)
    gps = class_gps.Gps()
    yolo = class_yolo()
    # phase define
    subthrea = subthread.Subthread(pressure=pressure, geomag=geomag, gps=gps, distance=distance, motor=motor)
    land = phase_land.Land(sky=0.1, land=0.01, pressure=pressure, subthread=subthrea)
    deployment = phase_deployment.Deploy(motor, nicrom, distance, geomag, subthrea)
    gps_phase = phase_gps.Gps_phase(motor, gps, geomag, subthrea)
    camera = phase_camera.Phase_camera(yolo, geomag, gps, motor, distance, subthrea)
    distance_phase = phase_distance.Distance_phase(distance, motor, geomag, subthrea)
    # main code
    try:
        goal = False
        land.run()
        deployment.run()
        while True:
            gps_phase.run(50)
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
        print("forced termination.")
        motor.end()
        print("GPIO closed.")
        print("not enjoy.")

if __name__ == "__main__":
    main()
