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
    try:
        print("Pressure testing")
        for i in range(15):
            pressure.read()
            print(f"data:{pressure.pressure}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Pressure skip")

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
    try:
        print("GeoMagnetic testing...")
        for i in range(150):
            try:
                geomag.get()
                print('Magnetometer (gauss): ({0:10.3f}, {1:10.3f}, {2:10.3f})'.format(geomag.x, geomag.y, geomag.z))
                print(geomag.theta_absolute)
                time.sleep(0.1)
            except KeyboardInterrupt:
                break
    except KeyboardInterrupt:
        print("GeoMagnetic skip")

    print("\nMotor importing...")
    motor = class_motor.Motor(geomag=geomag)
    print("success")
    print("Motor testing")
    for i in [10, 15, 20, 25, 30]:
        try:
            print(f"forward duty {i} testing...")
            for j in range(5):
                print(f"count down: {5-j}")
                time.sleep(1)
            motor.forward(i, i, 0.05, tick_dutymax=5)
        except KeyboardInterrupt:
            motor.changeduty(0, 0)
            print(f"forward duty {i} skip")
        time.sleep(1)
    for i in [10, 15, 20]:
        for j in [30, 60, 90]:
            try:
                print(f"rotate duty {i} {j}deg testing...")
                for k in range(5):
                    print(f"count down: {5-k}")
                    time.sleep(1)
                motor.rotate(j, i)
            except KeyboardInterrupt:
                motor.changeduty(0, 0)
                print(f"rotate duty {i} {j}deg skip")
            time.sleep(1)
    motor.end()

    print("\nDistance importing...")
    distance = class_distance.Distance()
    print("success")
    try:
        print("Distance testing")
        for i in range(15):
            distance.reading()
            print(f"distance:{distance.distance}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Distance skip")

    print("\nGps importing...")
    gps = class_gps.Gps()
    print("success")
    try:
        print("Gps testing")
        for i in range(30):
            print(f"lati:{gps.latitude}, longi:{gps.longitude}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Gps skip")

    print("\nCornDetect importing...")
    past = time.time()
    yolo = class_yolo.CornDetect()
    print(f"success. time:{time.time()-past}")
    while True:
        image = yolo.agnostic_nmstake_photo()
        c1, c2, estimated_image = yolo.test.estimate(image)
        adjusted_image, _, _ = yolo.automatic_brightness_and_contrast(estimated_image)
        print(c1, c2)

        cv2.imshow('estimated image', estimated_image)
        cv2.imshow('adjusted image', adjusted_image)

        key = cv2.waitKey(0)
        if key == ord('q'):
            break


if __name__ == "__main__":
    main()
