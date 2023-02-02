# GPS class
import serial
import micropyGPS
import threading
import time

class Gps:
    def __init__(self):
        self.gps = micropyGPS.MicropyGPS(9, 'dd') # MicroGPSオブジェクトを生成する。
                                                  # 引数はタイムゾーンの時差と出力フォーマット
        #gpsthread = threading.Thread(target=self.rungps, args=()) # 上の関数を実行するスレッドを生成
        #gpsthread.daemon = True
        #gpsthread.start() # スレッドを起動
        self.ser = serial.Serial('/dev/serial0', 9600, timeout=1)
        self.ser.readline() # 最初の1行は中途半端なデーターが読めることがあるので、捨てる

    def getgps(self):
        s = self.ser.read_all().decode("utf-8")
        for x in reversed(s):
            self.gps.update(x)
        self.latitude = self.gps.latitude[0]
        self.longitude = self.gps.longitude[0]
        
    
    """サブスレッド用
    def rungps(self): # GPSモジュールを読み、GPSオブジェクトを更新する
        self.s = serial.Serial('/dev/serial0', 9600, timeout=10)
        self.s.readline() # 最初の1行は中途半端なデーターが読めることがあるので、捨てる
        while True:
            sentence = self.s.readline().decode('utf-8') # GPSデーターを読み、文字列に変換する
            if sentence[0] != '$': # 先頭が'$'でなければ捨てる
                continue
            for x in sentence: # 読んだ文字列を解析してGPSオブジェクトにデーターを追加、更新する
                self.gps.update(x)

    def getgps(self):
        h = self.gps.timestamp[0] if self.gps.timestamp[0] < 24 else self.gps.timestamp[0] - 24
        #print('%2d:%02d:%04.1f' % (h, gps.timestamp[1], gps.timestamp[2]))
        #print('緯度経度: %2.8f, %2.8f' % (gps.latitude[0], gps.longitude[0]))
        self.gps_latitude = self.gps.latitude[0]
        self.gps_longitude = self.gps.longitude[0]
        #print('海抜: %f' % gps.altitude)
        #print(gps.satellites_used)
        #print('衛星番号: (仰角, 方位角, SN比)')
        #for k, v in gps.satellite_data.items():
        #    print('%d: %s' % (k, v))
        #print('')
        #print(gps_latitude)
        #print(gps_longitude)
    """
            
def main():
    gps = Gps()
    while True:
        #if gps.gps.clean_sentences > 20: # ちゃんとしたデータがある程度たまったら出力する
        start = time.time()
        gps.getgps()
        end = time.time()
        print(f"lati:{gps.latitude}, longi:{gps.longitude}, processTime:{end-start}")
        h = gps.gps.timestamp[0] if gps.gps.timestamp[0] < 24 else gps.gps.timestamp[0] - 24
        print('%2d:%02d:%04.1f' % (h, gps.gps.timestamp[1], gps.gps.timestamp[2]))
        time.sleep(30.0)

if __name__ == "__main__":
    main()
    pass
