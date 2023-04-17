import machine
import ssd1306
import time
from pyb import ADC, Pin, Timer

# Alim I2C
i2c = machine.SoftI2C(scl=machine.Pin('A15'), sda=machine.Pin('C10'))
machine.Pin('C13', machine.Pin.OUT).low()  # active le courant entrant
machine.Pin('A8', machine.Pin.OUT).high()  # active le courant sortant
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

# ADC = read sensor
Pin(Pin.cpu.C0, mode=Pin.ANALOG)
adc = ADC(Pin('C0'))

rtc = machine.RTC()
dt = rtc.datetime((2023, 04, 16, 3, 14, 00, 0, 0))
print(rtc.datetime())

MAX_HISTORY_BPM = 250
TOTAL_BEATS = 30

HEART = [
[ 0, 0, 0, 0, 0, 0, 0, 0, 0],
[ 0, 1, 1, 0, 0, 0, 1, 1, 0],
[ 1, 1, 1, 1, 0, 1, 1, 1, 1],
[ 1, 1, 1, 1, 1, 1, 1, 1, 1],
[ 1, 1, 1, 1, 1, 1, 1, 1, 1],
[ 0, 1, 1, 1, 1, 1, 1, 1, 0],
[ 0, 0, 1, 1, 1, 1, 1, 0, 0],
[ 0, 0, 0, 1, 1, 1, 0, 0, 0],
[ 0, 0, 0, 0, 1, 0, 0, 0, 0],
]

last_ord = 0

def refresh_oled(bpm, beat, value, mini, maxi):
    global last_ord

    oled.vline(0, 0, 32, 0)
    oled.scroll(-1, 0)

    if maxi - mini > 0:
        ord = 32 - int(16 * (value - mini) / (maxi - mini))
        oled.line(125, last_ord, 126, ord, 1)
        last_ord = ord

    oled.fill_rect(0, 0, 128, 16, 0)

    if bpm:
        oled.text("%d bpm" % bpm, 12, 0)

    if beat:
        for ord, row in enumerate(HEART):
            for x, c in enumerate(row):
                oled.pixel(x, ord, c)

    dt = rtc.datetime()
    dt[4]
    dt[5]
    
    oled.text(str(dt[4]) + ":", 80, 0)

    if dt[5] < 10 :
        oled.text("0" + str(dt[5]), 105, 0)
    else :
        oled.text(str(dt[5]), 105, 0)

    oled.show()

def calcule_bpm(beats) :
    if beats:
        beat_time = beats[-1] - beats[0]
        if beat_time:
            return (len(beats) / (beat_time)) * 60
        
timer = Timer(1)
timer.init(period=10000, callback=calcule_bpm)

def detect():

    history_bpm = []
    beats = []
    beat = False 
    bpm = None

    oled.fill(0)

    while True :
        value = adc.read()
        print(value) 
        history_bpm.append(value)
        history_bpm = history_bpm[-MAX_HISTORY_BPM:]

        mini, maxi = min(history_bpm), max(history_bpm)

        threshold_on = (mini + maxi * 3) // 4
        threshold_off = (mini + maxi) // 2

        if  value > threshold_on and beat == False:
            beat = True
            beats.append(time.time())
            beats = beats[-TOTAL_BEATS:]
            bpm = calcule_bpm(beats)

        if value < threshold_off and beat == True:
            beat = False
    
        refresh_oled(bpm, beat, value, mini, maxi)

detect()
