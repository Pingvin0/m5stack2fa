from machine import Pin,deepsleep,RTC
import machine
import esp32
from utime import sleep
import ntptime
import socket
import utime
wlssid = "TP-Link_MAIN_Guest"
wlpw = "1964370737"


def connectToWifi():
    import network
    print("Connecting to wifi")
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    sta_if.connect(wlssid, wlpw)
    led = Pin(2, Pin.OUT)
    while sta_if.isconnected() == False:
        print("Unconnected to wifi")
        led.value(1)
        sleep(0.2)
        led.value(0)
        sleep(0.2)
    print("Successful connection to " + wlssid)
    led.value(0)
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
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()

def syncTime():
    ntptime.settime()

def goSleepBoi():
    wakePin =  Pin(0, Pin.IN, Pin.PULL_DOWN)
    esp32.wake_on_ext0(wakePin, esp32.WAKEUP_ALL_LOW)
    print("Going to sleep in 5s")
    sleep(5)
    print("Going to sleep")
    deepsleep()

def sendTimeToMQTT():
    year,month,day,idk,hour,minute,second,microsecond = RTC().datetime()
    http_get("https://api.thingspeak.com/update?api_key=45TGY41GRUYV83SK&field1=" + str(hour) + ":" + str(minute))
    
def sendSleepToMQTT():
    http_get("https://api.thingspeak.com/update?api_key=45TGY41GRUYV83SK&field2=1")
    
def sendConnectedToMQTT():
    http_get("https://api.thingspeak.com/update?api_key=45TGY41GRUYV83SK&field3=1")

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    led = Pin(2, Pin.OUT)
    year,month,day,idk,hour,minute,second,microsecond = RTC().datetime()
    if minute < 10:
        minute = "0" + str(minute)
    print('woke from a deep sleep time is: ' + str(hour) + ":" + str(minute) + " And the date is (YYYY/MM/DD) " + str(year) + "/" + str(month) + "/" + str(day))
    led.value(1)
else:
    print('power on or hard reset')
    
    connectToWifi()
    syncTime()
    sendTimeToMQTT()
    print("Current time detected as: " +  str(RTC().datetime()))
    
    sendSleepToMQTT()
    goSleepBoi()

