# drv8835 並列接続
# IN/IN mode動作テスト
# IN/IN modeはCoast(空転)があり，慣性的な原則でドライバに優しい
# out1が+，out2が-になるように配線する

import RPi.GPIO as GPIO
import time

def forward(): # IN1を1，IN2を0にする
    print("start0")
    pwmIN1.start(0)
    pwmIN2.start(0)
    print("for")
    for i in range(10):
        pwmIN1.ChangeDutyCycle(duty/10*(i+1))
        time.sleep(duty/10)

def reverse(): # IN1を0，IN2を1にする
    pwmIN1.start(0)
    pwmIN2.start(0)
    for i in range(10):
        pwmIN2.ChangeDutyCycle(duty/10*(i+1))
        time.sleep(duty/10)

def stop(pin):
    for i in range(10):
        pin.ChangeDutyCycle(duty*(1-(i+1)/10))
        time.sleep(duty/10)

IN1 = 24
IN2 = 23

t = 3 # [s]
pwm = 50 # Hz
duty = 60 # duty比
# GPIO.setmode(GPIO.BOARD) # 物理的な番号を指定するように設定
try:
    print("setup")
    GPIO.setmode(GPIO.BCM) # GPIOnを指定するように設定
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    pwmIN1 = GPIO.PWM(IN1, pwm) # pin, Hz
    pwmIN2 = GPIO.PWM(IN2, pwm) # pin, Hz
    
    print("forward start")
    forward()
    print("sleep")
    time.sleep(t)
    print("stop")
    stop(pwmIN1)
    time.sleep(t)
    print("forward fin.\nreverse start")
    reverse()
    time.sleep(t)
    stop(pwmIN2)
    time.sleep(t)
    print("reverse fin.")
    
    # モータ初期化
    GPIO.cleanup()
except KeyboardInterrupt:
    pwmIN1.stop()
    pwmIN2.stop()
    GPIO.output(IN1, False)
    GPIO.output(IN2, False)
    GPIO.cleanup()
    print("finish")
