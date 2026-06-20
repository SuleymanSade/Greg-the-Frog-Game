import serial
import math
import time

PORT = "COM7"
SERIAL_RATE = 9600

allHistory = []
ser = serial.Serial(port = PORT, baudrate=SERIAL_RATE, timeout=1)

def get_data():
    # Set: x-val, y-val, hearth rate
    clean = "-1, -1, -1" # TODO: put the number of commmas for the default val

    raw = ser.readline()

    while raw:
        # raw = ser.read_all()
        clean = raw.decode('utf-8', errors='ignore').strip()
        print(clean)
    data = clean.split(", ")

    # for i in range(1):
    #     if data[i] == '-1':
    #         data[i] = None
    #     else:
    #         data[i] = int(data[i])

    return data


def detect_flick():
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
        deg = math.atan2(motion[0]-512, motion[1]-512)
    
    return deg
    
time.sleep(2)
while True:
    data = get_data()

    # if data[0] is not None and data[1] is not None:
    #     allHistory.append(data)

    # if len(allHistory) >= 2:
    #     print(detect_flick())