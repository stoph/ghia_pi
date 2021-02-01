#!/usr/bin/env python

import RPi.GPIO as GPIO
import os, time, sys, subprocess, threading, serial, random
from rotary_class import RotaryEncoder

# Define GPIO numbers for buttons
button1_pin = 5
button2_pin = 6
button3_pin = 12
button4_pin = 13
button5_pin = 26
volume_pin_a = 17
volume_pin_b = 16
volume_pin_mute = 4

# Define default volume change
vol_change = "5"

# Assign GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button3_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button4_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button5_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

  

# Set up Serial
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
ser.flush()

# Handle Ctrl-c to exit.
from signal import signal, SIGINT
from sys import exit
def signal_handler(signal_received, frame):
    print(signal_received)
    exit(0)
signal(SIGINT, signal_handler)

# Button Debouncer
class ButtonHandler(threading.Thread):
    # https://raspberrypi.stackexchange.com/a/76738/
    def __init__(self, pin, func, edge='both', bouncetime=200):
        super().__init__(daemon=True)

        self.edge = edge
        self.func = func
        self.pin = pin
        self.bouncetime = float(bouncetime)/1000

        self.lastpinval = GPIO.input(self.pin)
        self.lock = threading.Lock()

    def __call__(self, *args):
        if not self.lock.acquire(blocking=False):
            return

        t = threading.Timer(self.bouncetime, self.read, args=args)
        t.start()

    def read(self, *args):
        pinval = GPIO.input(self.pin)

        if (
                ((pinval == 0 and self.lastpinval == 1) and
                 (self.edge in ['falling', 'both'])) or
                ((pinval == 1 and self.lastpinval == 0) and
                 (self.edge in ['rising', 'both']))
        ):
            self.func(*args)

        self.lastpinval = pinval
        self.lock.release()

# Audio functions
def mute():
    os.system('amixer sset Digital toggle')

def previous_track():
    os.system('dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_F0_C3_71_79_14_05 org.bluez.MediaControl1.Previous')

def next_track():
    os.system('dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_F0_C3_71_79_14_05 org.bluez.MediaControl1.Next')

def play_pause():
    print('play_pause')
    if str(subprocess.check_output("dbus-send --system --type=method_call --print-reply --dest=org.bluez /org/bluez/hci0/dev_F0_C3_71_79_14_05/player0 org.freedesktop.DBus.Properties.Get string:org.bluez.MediaPlayer1 string:'Status'", shell=True)).find("playing") > 0:
        pause()
    else:
        play()

def play():
    os.system('dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_F0_C3_71_79_14_05 org.bluez.MediaControl1.Play')

def pause():
    os.system('dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_F0_C3_71_79_14_05 org.bluez.MediaControl1.Pause')

def volume_up(vol=vol_change):
    print('volume up:' + vol)
    os.system('amixer sset Digital ' + vol + '%+')

def volume_down(vol=vol_change):
    print('volume up:' + vol)
    os.system('amixer sset Digital ' + vol + '%-')

def set_volume(vol):
    print('set_volume:' + vol)
    os.system('amixer sset Digital ' + vol + '%')

def party():
    print('party')
    colorList = ['red', 'green', 'blue']
    color = random.choice(colorList) + "\n"
    print(color)
    ser.write(str.encode(color))
    ser.flush()

# Button functions
def button1(x):
    print("1")
    #mute()
def button2(x):
    print("2")
    previous_track()
def button3(x):
    print("3")
    next_track()
def button4(x):
    print("4")
    party()
def button5(x):
    print("5")
    play_pause()

def volume_event(event):
    if event == RotaryEncoder.CLOCKWISE:
        print ("clockwise", RotaryEncoder.CLOCKWISE)
        volume_up()
    elif event == RotaryEncoder.ANTICLOCKWISE:
        print ("anticlockwise", RotaryEncoder.ANTICLOCKWISE)
        volume_down()
    elif event == RotaryEncoder.BUTTONDOWN:
        print ("button down", RotaryEncoder.BUTTONDOWN)
        mute()
    elif event == RotaryEncoder.BUTTONUP:
        print ("button up", RotaryEncoder.BUTTONUP)
    return

# Assign callback functions
cb1 = ButtonHandler(button1_pin, button1, edge='rising', bouncetime=10)
cb1.start()
GPIO.add_event_detect(button1_pin, GPIO.RISING, callback=cb1)
cb2 = ButtonHandler(button2_pin, button2, edge='rising', bouncetime=100)
cb2.start()
GPIO.add_event_detect(button2_pin, GPIO.RISING, callback=cb2)
cb3 = ButtonHandler(button3_pin, button3, edge='rising', bouncetime=100)
cb3.start()
GPIO.add_event_detect(button3_pin, GPIO.RISING, callback=cb3)
cb4 = ButtonHandler(button4_pin, button4, edge='rising', bouncetime=100)
cb4.start()
GPIO.add_event_detect(button4_pin, GPIO.RISING, callback=cb4)
cb5 = ButtonHandler(button5_pin, button5, edge='rising', bouncetime=100)
cb5.start()
GPIO.add_event_detect(button5_pin, GPIO.RISING, callback=cb5)

# Assign Volume Callback functions
volumeknob = RotaryEncoder(volume_pin_a,volume_pin_b,volume_pin_mute,volume_event)

while True:
    time.sleep(.05)
    #pass
