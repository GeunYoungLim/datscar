import RPi.GPIO as GPIO
from time import sleep
from tkinter import *

from remote.command import Receiver
import argparse

import subprocess

MOTOR1A = 22 # Front_back Motor PIN number, PIN color-White
MOTOR1B = 24 # Front_back Motor PIN number, PIN color-blue,green

MOTOR2A = 23 # left_right Motor PIN number, PIN color-blue 
MOTOR2B = 25 # left_right Motor PIN number, PIN color-brown
#--------------------------------------------

pwmpin1 = 12
pwmpin2 = 13
pwm_freq = 20*1000  # PWM frequence 20kHz standard
duty1 = 0
duty2 = 0

#--------------------------------------------

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOTOR1A, GPIO.OUT)
GPIO.setup(MOTOR1B, GPIO.OUT)
GPIO.setup(MOTOR2A, GPIO.OUT)
GPIO.setup(MOTOR2B, GPIO.OUT)
GPIO.setup(pwmpin1, GPIO.OUT)   #PWM_ control PIN1
GPIO.setup(pwmpin2, GPIO.OUT)   #PWM_ control PIN2
p1 = GPIO.PWM(pwmpin1,  pwm_freq) # pwmPin1_frequence setting
p1.start( duty1 )
p2 = GPIO.PWM(pwmpin2,  pwm_freq) # pwmPin2_frequence setting
p2.start( duty2 )
tm = 0.02
left = 0
steer = 0

def recv_command(vector):
    global steer
    if vector == [0,1,0]:
        print('forward')
        duty1 = 30
        p1.ChangeDutyCycle(duty1 )
        GPIO.output(MOTOR1A, 1)
        GPIO.output(MOTOR1B, 0)
        
        if steer > 0:
            # right
            steer -= 1
            if steer < 0:
                steer = 0
            left = 1
            duty = 20
            p2.ChangeDutyCycle(duty)
            GPIO.output(MOTOR2A, 1)
            GPIO.output(MOTOR2B, 0)
        elif steer < 0:
            # left 
            steer += 1
            if steer > 0:
                steer = 0
            right = 1
            duty = 20
            p2.ChangeDutyCycle(duty)
            GPIO.output(MOTOR2A, 0)
            GPIO.output(MOTOR2B, 1)

    if vector == [1,0,0]:
        print('left')
        steer -=1
        if steer < -3 :
            steer = -3
        left = 1
        duty2 =20 
        p2.ChangeDutyCycle(duty2)
        GPIO.output(MOTOR2A,1)
        GPIO.output(MOTOR2B,0)
    if vector == [0,0,1]:
        print('right')
        steer += 1
        if steer > 3:
            steer = 3
        right = 1
        duty2 = 20 
        p2.ChangeDutyCycle(duty2)
        GPIO.output(MOTOR2A,1)
        GPIO.output(MOTOR2B,1)
    if vector == [0, 0, 0]:
        print('stop')
        return

if __name__ == '__main__':
    args = argparse.ArgumentParser()

    args.add_argument('--stream', type=str, default='cloud.inspace.co.kr:9000')
    args.add_argument('--control', type=str, default='cloud.inspace.co.kr:8000')
    args.add_argument('--videoinput', type=str, default='0')

    config = args.parse_args()
    stream_url, stream_port = config.stream.split(':')
    control_url, control_port = config.control.split(':')



    ffmpeg = ['ffmpeg',
              '-r','30',
              '-s', '640x480',
              '-an',
              '-i', config.videoinput,
              '-f', 'mpegts',
              'udp://{}:{}'.format(stream_url, stream_port)]
    with subprocess.Popen(ffmpeg) as proc:
        print(proc.args)
        receiver = Receiver(control_url, control_port)
        receiver.set_recv_callback(recv_command)
        receiver.connect()
