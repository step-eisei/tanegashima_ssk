import class_pressure
import time

class Land:
    
    def __init__(self, sky=0.1, land=0.01): #地上気圧測定
        self.sky=sky
        self.land=land
        self.i=0
        while self.i<=10:
            get_pressure=class_pressure.Pressure()
            get_pressure.read()
            sum_pressure = sum_pressure + get_pressure.pressure
            self.i=self.i+1
        self.land=sum_pressure/10
        self.i=0

    def sky_pressure(self):
        self.i=0
        while self.i<=10:
            get_pressure=class_pressure.Pressure()
            get_pressure.read() #毎回pressure更新
            if self.land - get_pressure.pressure > self.sky: #閾値暫定
                print(self.i)
                self.i=self.i+1
            else: self.i=0 #やり直し
            time.sleep(0.1)
        print("sky")
        self.i=0

    def land_pressure(self):
        self.i=0
        while self.i<=10:
            get_pressure=class_pressure.Pressure()
            get_pressure.read() #毎回pressure更新
            if get_pressure.pressure - self.land < self.land: #閾値暫定
                print(self.i)
                self.i=self.i+1
            else: self.i=0 #やり直し
            time.sleep(0.1)
        print("land")

    def run(self):
        self.sky_pressure()
        self.land_pressure()

def main(sky=0.1, land=0.01): #上空判定，地上判定の閾値
    land_check=Land(sky, land) #land更新
    land_check.run()


if __name__ == "__main__":
    main()
    pass
