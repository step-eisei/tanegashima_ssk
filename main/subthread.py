# サブスレッド処理
import class_pressure
import class_geomag
import class_gps
import class_distance
import class_motor
import datetime
import time
import threading
import csv

class Subthread:
    
    def __init__(self, pressure=class_pressure.Pressure(), geomag=class_geomag.GeoMagnetic(), gps=class_gps.Gps(), distance=class_distance.Distance(), motor=class_motor.Motor()):
        self.pressure = pressure
        self.geomag = geomag
        self.gps = gps
        self.distance = distance
        self.motor = motor
        self.time_start = time.time()
        self.phase = 0
        self.phaselist = ["land", "deployment", "gps", "camera", "distance"]
        DIFF_JST_FROM_UTC = 9
        jp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
        self.recordname = 'record/record_' + str(jp_time).replace(' ', '_').replace(':', '-').replace('.', '_') + '.csv'
        with open(self.recordname, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["comment", "time", "phase", "balo", "latitude", "longitude", "duty_R", "duty_L", "theta", "corn", "distance"])
    
    def record(self, loop=False, comment="threading"):
        while(True):
            pass
            time_now = time.time()
            with open(self.recordname, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([comment, time_now-self.time_start, self.phaselist[self.phase], self.pressure.pressure, self.gps.latitude, self.gps.longitude, self.motor.duty_R_now, self.motor.duty_L_now, self.geomag.theta_absolute, "corn", self.distance.distance])
            print("regularly record.")
            if(loop): time.sleep(10)
            else: break
    
    def run(self):
        self.thread = threading.Thread(target=self.record(True))
        self.thread.setDaemon(True)
        self.thread.start()
        print("threading start.")

def main():
    try:
        subthread = Subthread()
        subthread.run()
        while True:
            print("processing...")
            time.sleep(10)
    except KeyboardInterrupt:
        subthread.motor.end()
        print("terminated.")

if __name__ == "__main__":
    main()
    pass
