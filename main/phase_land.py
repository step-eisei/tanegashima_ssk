import class_pressure
import subthread
import time

class Land:
    
    def __init__(self,get_pressure=None,subth=None,sky=0.1, land=0.2): #地上気圧測定
        if get_pressure == None: self.get_pressure = class_pressure.Pressure()
        else:                    self.get_pressure = get_pressure

        if subth == None:        self.subth = subthread.Subthread(pressure=self.get_pressure)
        else:                    self.subth = subth

        self.sky=sky   #上空まで上がったか判定するときの大気圧の変化の閾値 要調整
        self.land=land #地上まで降りたか、判定するときの大気圧の変化の閾値 要調整

        #最初に地上の大気圧を測る
        i=0
        sum_pressure=0.0
        while i<10:
            self.get_pressure.read()
            sum_pressure = sum_pressure + self.get_pressure.pressure
            i=i+1
            time.sleep(0.5)
        self.start_pressure=sum_pressure/10
        print(self.start_pressure)
    
    #上空に上がったか判定
    def sky_pressure(self):
        i=0
        while i<=10:
            self.get_pressure.read() #毎回pressure更新
            print(self.get_pressure.pressure)
            if self.start_pressure-self.get_pressure.pressure > self.sky: #閾値暫定
                print(i)
                i = i + 1
            else: 
                i=0 #やり直し
                print("yet")
            time.sleep(0.5)
        print("sky")
    
    #地上まで降りたか判定
    def land_pressure(self):
        i=0
        while i<=10:
            self.get_pressure.read() #毎回pressure更新
            print(self.get_pressure.pressure)
            if self.start_pressure-self.get_pressure.pressure < self.land: #閾値暫定
                print(i)
                i=i+1
            else:
                i=0 #やり直し
                print("yet")
            time.sleep(0.5)
        print("land")

    def run(self):
        self.subth.phase=0
        self.sky_pressure()
        self.subth.record(comment="sky")
        self.land_pressure()
        self.subth.record(comment="land")

def main(sky=0.1, land=0.01): #上空判定，地上判定の閾値
    try:
        land_check=Land(sky=sky, land=land) #land更新
        print("start")
        land_check.run()
    except KeyboardInterrupt:
        print("\nInterrupted.")


if __name__ == "__main__":
    main()