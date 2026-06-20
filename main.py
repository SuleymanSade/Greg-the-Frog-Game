import tkinter as tk
import serial
import math

PORT = "COM3"
SERIAL_RATE = 9600

JYSTCK_LOWER = 450
JYSTCK_HIGHER = 550

allHistory = []

def get_data():
    # Set: x-val, y-val, hearth rate
    clean = "NULL, NULL, NULL" # TODO: put the number of commmas for the default val

    ser = serial.Serial(port = PORT, baudrate=SERIAL_RATE, timeout=1)

    while ser.in_waiting > 0:
        raw = ser.readline()
        clean = raw.decode('utf-8').strip()
    data = clean.split(", ")

    return data


def detect_flick():
    global allHistory
    motion = []
    isExtX = False
    isExtY = False

    if allHistory[-1][0] < 550 and allHistory[-1][0] > 450:
        if allHistory[-2][0] > 550 or allHistory[-2][0] < 450:
            isExtX = True
    if allHistory[-1][1] < 550 and allHistory[-1][1] > 450:
        if allHistory[-2][1] > 550 or allHistory[-2][1] < 450:
            isExtY = True

    deg = None

    if isExtX or isExtY:
        motion[0] = allHistory[-2][0]
        motion[1] = allHistory[-2][1]
        deg = math.atan(motion[0]-512, motion[1]-512)
    
    return deg

root = tk.Tk()

def loop():
    data = get_data()
    if get_data[0] != "NULL":
        allHistory.append(get_data())
    
    deg = detect_flick()

    if deg is not None:
        # The action of moving the frog
        pass
    else:
        #Stay at the same pos
        pass

    root.after(40, loop)

loop()
root.mainloop() 