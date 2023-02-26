# main code in tanegashima 2023!

# class import
import class_pressure
import class_nicrom
import class_motor
import class_distance
import class_gps
import class_geomag
import class_yolo
# others
import time
import csv
import cv2

def main():
    # class define
    print("\nPressure importing...")
    pressure = class_pressure.Pressure()
    print("success")
    print("Pressure testing")
    for i in range(10):
        pressure.read()
        print(f"data:{pressure.pressure}")
        time.sleep(0.5)

    print("\nNicrom importing...")
    nicrom = class_nicrom.Nicrom(pin=21)
    print("success")
    try:
        print("Nicrom testing")
        for i in range(5):
            print(f"count down: {5-i}")
            time.sleep(1)
        print("10 sec. heating...")
        nicrom.heat(10)
        print("fin. GPIO end")
        nicrom.end()
    except KeyboardInterrupt:
        nicrom.end()
        print("Nicrom skip")

    print("\nGeoMagnetic importing...")
    with open ('calibration_lsm303.csv', 'r') as f :# goal座標取得プログラムより取得
        reader = csv.reader(f)
        line = [row for row in reader]
        rads = [float(line[1][i]) for i in range(3)]
        aves = [float(line[2][i]) for i in range(3)]
    geomag = class_geomag.GeoMagnetic(True, rads, aves)
    print("success")
    print("GeoMagnetic testing")
    for i in range(50):
        geomag.get()
        print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(geomag.x, geomag.y, geomag.z))
        print(geomag.theta_absolute)
        time.sleep(0.1)

    print("\nMotor importing...")
    motor = class_motor.Motor(geomag=geomag)
    print("success")
    print("Motor testing")
    print(f"forward duty 20 testing...")
    motor.forward(20, 20, 0.05, tick_dutymax=5)
    motor.changeduty(0, 0)
    time.sleep(2)
    print(f"rotate duty 15 45deg testing...")
    motor.rotate(45, 15)
    motor.changeduty(0, 0)
    motor.end()

    print("\nDistance importing...")
    distance = class_distance.Distance()
    print("success")
    print("Distance testing")
    for i in range(10):
        distance.reading()
        print(f"distance:{distance.distance}")
        time.sleep(0.5)

    print("\nGps importing...")
    gps = class_gps.Gps()
    print("success")
    print("Gps testing")
    for i in range(20):
        print(f"lati:{gps.latitude}, longi:{gps.longitude}")
        time.sleep(0.5)
    
    print("camera test")
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    #camera.set(cv2.CAP_PROP_AUTO_WB, 1)
    #camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    success, image = camera.read()
    if not success:
        print("camera failed")
    else:
        while True:
            #image = cv2.convertScaleAbs(image, alpha=1.0, beta=-50)
            #image, _, _ = automatic_brightness_and_contrast(image)
            success, image = camera.read()
            cv2.imshow('image', image)
            key = cv2.waitKey(1)
            if key == ord('q'): 
                break
    cv2.destroyWindow('image')
    camera.release()

    print("\nCornDetect importing...")
    past = time.time()
    yolo = class_yolo.CornDetect()
    print(f"success. time:{time.time()-past}")
    while True:
        image = yolo.take_photo()
        c1, c2, estimated_image = yolo.test.estimate(image)
        adjusted_image, _, _ = yolo.automatic_brightness_and_contrast(estimated_image)
        print(c1, c2)

        cv2.imshow('estimated image', estimated_image)
        cv2.imshow('adjusted image', adjusted_image)

        key = cv2.waitKey(0)
        if key == ord('q'):
            break
    camera.release()


if __name__ == "__main__":
    main()
