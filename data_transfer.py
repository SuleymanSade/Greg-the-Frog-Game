import serial
import math
import time

PORT = "COM7"
SERIAL_RATE = 9600

allHistory = []
ser = serial.Serial(port = PORT, baudrate=SERIAL_RATE, timeout=1)

def send_data(info: str):
    # May need thereading
    ser.write(info)

def get_data():
    # Set: x-val, y-val, hearth rate
    clean = "-1, -1" # TODO: put the number of commmas for the default val

    raw = ser.readline()

    if raw:
        # raw = ser.read_all()
        clean = raw.decode('utf-8', errors='ignore').strip()
        # print(clean)
    data = clean.split(", ")

    for i in range(1):
        if data[i] == '-1':
            data[i] = None
        elif data[i] == '':
            data[i] = 0
        else:
            data[i] = int(data[i])
        # print(data[i], end=", ")

    return data


def detect_flick():
    # if type(allHistory[-1][0]) is str or type(allHistory[-2][0]) is str or type(allHistory[-1][1]) is str or type(allHistory[-2][1]) is str:
    #     return None
    motion = [0,0]
    isExtX = False
    isExtY = False

    if int(allHistory[-1][0]) < 550 and int(allHistory[-1][0]) > 450:
        if int(allHistory[-2][0]) > 550 or int(allHistory[-2][0]) < 450:
            isExtX = True
    if int(allHistory[-1][1]) < 550 and int(allHistory[-1][1]) > 450:
        if int(allHistory[-2][1]) > 550 or int(allHistory[-2][1]) < 450:
            isExtY = True

    deg = None

    if isExtX or isExtY:
        motion[0] = allHistory[-2][0]
        motion[1] = allHistory[-2][1]
        deg = math.atan2(int(motion[0])-512, int(motion[1])-512)
    
    return deg / (math.pi) * 180
    
time.sleep(2)
while True:
    data = get_data()

    if data[0] is not None and data[1] is not None:
        allHistory.append(data)

    if len(allHistory) >= 2:
        flick = detect_flick()
        if flick is not None:
            print(flick/ (math.pi) * 180)