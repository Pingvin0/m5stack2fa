from machine import Pin,deepsleep,RTC
import machine
import esp32
from utime import sleep
import socket
import utime
import sys
import m5stack
from m5stack import lcd

sys.path.insert(1, '')
import ntptime
wlssid = "TP-Link_MAIN_Guest"
wlpw = "1964370737"
rtc = machine.RTC()


def turnOnScreen():
    m5stack.lcd.clear()
    m5stack.axp.setLcdBrightness(35)

def turnOffScreen():
    m5stack.lcd.clear()
    m5stack.axp.setLcdBrightness(0)

def connectToWifi():
    import network
    print("Connecting to wifi")
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    sta_if.connect(wlssid, wlpw)
    while sta_if.isconnected() == False:
        print("Unconnected to wifi")
        sleep(0.2)
    print("Successful connection to " + wlssid)
    sendConnectedToMQTT()

def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print("Got data from http")
        else:
            break
    print("Sent httpget")
    s.close()

def syncTime():
    ntptime.settime()

def goSleepBoi():
    wakePin =  Pin(37, Pin.IN, Pin.PULL_DOWN)
    esp32.wake_on_ext0(wakePin, esp32.WAKEUP_ALL_LOW)
    print("Going to sleep in 3s")
    sleep(3)
    print("Going to sleep")
    turnOffScreen()
    deepsleep()

def sendTimeToMQTT():
    year,month,day,idk,hour,minute,second,microsecond = utime.localtime()
    http_get("https://api.thingspeak.com/update?api_key=45TGY41GRUYV83SK&field1=" + str(hour) + "H" + str(minute) + "M")
    
def sendSleepToMQTT():
    http_get("https://api.thingspeak.com/update?api_key=45TGY41GRUYV83SK&field2=1")
    
def sendConnectedToMQTT():
    http_get("https://api.thingspeak.com/update?api_key=45TGY41GRUYV83SK&field3=1")

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    turnOnScreen()
    lcd.text(0, 0, "DISCORD")
    lcd.text(lcd.CENTER, lcd.CENTER, "AUTHENTICATOR CODE HERE")
    year,month,day,idk,hour,minute,second,microsecond = utime.localtime()
    if minute < 10:
        minute = "0" + str(minute)
    print('woke from a deep sleep time is: ' + str(hour) + ":" + str(minute) + " And the date is (YYYY/MM/DD) " + str(year) + "/" + str(month) + "/" + str(day))
    goSleepBoi()
else:
    print('power on or hard reset')
    
    connectToWifi()
    syncTime()
    sendTimeToMQTT()
    print("Current time detected as: " + str(utime.localtime()))
    
    sendSleepToMQTT()
    goSleepBoi()