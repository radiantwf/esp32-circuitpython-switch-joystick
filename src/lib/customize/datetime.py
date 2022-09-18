import time
import adafruit_ntp
import wifi
import socketpool
import rtc

def now():
    now = time.localtime()
    str = "%02d/%02d/%02d %02d:%02d:%02d" % (
        now[0], now[1], now[2], now[3], now[4], now[5])
    return str

def ntpSync():
    ntp = adafruit_ntp.NTP(socketpool.SocketPool(wifi.radio), server = '0.cn.pool.ntp.org', port=123, tz_offset=8)
    rtc.RTC().datetime = ntp.datetime
    return now()
