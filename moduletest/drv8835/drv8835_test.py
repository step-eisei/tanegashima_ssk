# 並列接続では絶対に使用しないこと!!
# coding: utf-8
import RPi.GPIO as GPIO
import time

MOTORPIN1 = 4
MOTORPIN2 = 5

GPIO.setwarnings(False)
GPIO.setmode( GPIO.BCM )
GPIO.setup(MOTORPIN1, GPIO.OUT )
GPIO.setup(MOTORPIN2, GPIO.OUT )

# PWM/100Hzに設定
ML1 = GPIO.PWM(MOTORPIN1, 100)
ML2 = GPIO.PWM(MOTORPIN2, 100)
# 初期化
ML1.start(0)
ML2.start(0)

if __name__ == '__main__':
    try:
        #モーター開始
        ML1.ChangeDutyCycle(10)
        ML2.ChangeDutyCycle(0)
        time.sleep(3)
        ML1.ChangeDutyCycle(20)
        ML2.ChangeDutyCycle(0)
        time.sleep(3)
        ML1.ChangeDutyCycle(50)
        ML2.ChangeDutyCycle(0)
        time.sleep(3)
        ML1.ChangeDutyCycle(100)
        ML2.ChangeDutyCycle(0)
        time.sleep(3)

        ML1.ChangeDutyCycle(0)
        ML2.ChangeDutyCycle(0)

        ML1.ChangeDutyCycle(0)
        ML2.ChangeDutyCycle(10)
        time.sleep(3)
        ML1.ChangeDutyCycle(0)
        ML2.ChangeDutyCycle(20)
        time.sleep(3)
        ML1.ChangeDutyCycle(0)
        ML2.ChangeDutyCycle(50)
        time.sleep(3)
        ML1.ChangeDutyCycle(0)
        ML2.ChangeDutyCycle(100)
        time.sleep(3)
        ML1.ChangeDutyCycle(0)
        ML2.ChangeDutyCycle(0)

        ML1.ChangeDutyCycle(100)
        ML2.ChangeDutyCycle(100)
        time.sleep(3)

        ML1.stop()
        ML2.stop()
    except KeyboardInterrupt:
        ML1.stop()
        ML2.stop()
        GPIO.cleanup()
        sys.exit(0)
