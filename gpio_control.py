import RPi.GPIO as GPIO
import os, time, sys, subprocess
import threading

# Define GPIO numbers for buttons
button1 = 5
button2 = 6
button3 = 13
button4 = 26
button5 = 12
#volume = 16

# Define default volume change
vol_change = 5


GPIO.setmode(GPIO.BCM)
GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button5, GPIO.IN)

# Handle Ctrl-c to exit.
from signal import signal, SIGINT
from sys import exit
def signal_handler(signal_received, frame):
    print(signal_received)
    exit(0)
signal(SIGINT, signal_handler)

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

def mute(x):
    os.system('amixer sset Digital toggle')

def previous_track(x):
    os.system('dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_F0_C3_71_79_14_05 org.bluez.MediaControl1.Previous')

def next_track(x):
    os.system('dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_F0_C3_71_79_14_05 org.bluez.MediaControl1.Next')

def party(x):
    print('party')

def play_pause(x):
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


# Button1 - Mute
cb1 = ButtonHandler(button1, mute, edge='rising', bouncetime=100)
cb1.start()
GPIO.add_event_detect(button1, GPIO.RISING, callback=cb1)
# Button2 - Previous Track
cb2 = ButtonHandler(button2, previous_track, edge='rising', bouncetime=100)
cb2.start()
GPIO.add_event_detect(button2, GPIO.RISING, callback=cb2)
# Button3 - Next Track
cb3 = ButtonHandler(button3, next_track, edge='rising', bouncetime=100)
cb3.start()
GPIO.add_event_detect(button3, GPIO.RISING, callback=cb3)
# Button4 - ??
cb4 = ButtonHandler(button4, play_pause, edge='rising', bouncetime=100)
cb4.start()
GPIO.add_event_detect(button4, GPIO.RISING, callback=cb4)
# Button5 - Play/Pause
cb5 = ButtonHandler(button5, play_pause, edge='rising', bouncetime=100)
cb5.start()
GPIO.add_event_detect(button5, GPIO.RISING, callback=cb5)

while True:
    pass
