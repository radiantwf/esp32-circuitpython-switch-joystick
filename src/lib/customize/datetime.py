import time

def now():
    now = time.localtime()
    str = "%02d/%02d/%02d %02d:%02d:%02d" % (
        now[0], now[1], now[2], now[3], now[4], now[5])
    return str


def ntpSync():
    try:
        import wifi
        import socketpool
        import rtc
        import adafruit_ntp
        ntp = adafruit_ntp.NTP(socketpool.SocketPool(
            wifi.radio), server='1.cn.pool.ntp.org', tz_offset=8)
        rtc.RTC().datetime = ntp.datetime
    except:
        pass
    return now()
