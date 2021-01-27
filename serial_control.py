# Need to use https://github.com/saiprasanth-m/Raspberry-Pi-BLE-Media-control

# Media-API: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc/media-api.txt

import serial, os

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    ser.flush()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            if line == 'play_pause':
                # dbus-send --system --type=method_call --print-reply --dest=org.bluez /org/bluez/hci0/dev_F0_C3_71_79_14_05/player0 org.freedesktop.DBus.Properties.Get string:org.bluez.MediaPlayer1 string:Status
                # possible values "playing", "stopped", "paused"
            elif line == 'play':
                os.system('dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_F0_C3_71_79_14_05 org.bluez.MediaControl1.Next')
            elif line == 'pause':
                os.system('dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_F0_C3_71_79_14_05 org.bluez.MediaControl1.Next')
            elif line == 'mute':
                os.system('amixer sset Digital toggle')
            elif line == 'next_track':
                os.system('dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_F0_C3_71_79_14_05 org.bluez.MediaControl1.Next')
            elif line == 'previous_track':
                os.system('dbus-send --system --print-reply --dest=org.bluez /org/bluez/hci0/dev_F0_C3_71_79_14_05 org.bluez.MediaControl1.Previous')
            elif line == 'volume_up':
                os.system('amixer sset Digital 5%+')
            elif 'volume_up ' in line:
                vol = line.split(None, 1)[1]
                os.system('amixer sset Digital ' + vol + '%+')
            elif line == 'volume_down':
                os.system('amixer sset Digital 5%-')
            elif 'volume_down ' in line:
                vol = line.split(None, 1)[1]
                os.system('amixer sset Digital ' + vol + '%-')
            elif 'volume ' in line:
                vol = line.split(None, 1)[1]
                os.system('amixer sset Digital ' + vol + '%')
            
