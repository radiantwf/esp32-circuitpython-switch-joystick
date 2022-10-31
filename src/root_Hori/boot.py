import usb_hid
import hid.device
import customize.datetime

device = hid.device.get_device(hid.device.Device_HORIPAD_S)
device.init_device()
try:
    import wifi
    import customize.wifi_connect as wifi_connect
    wifi_connect.connect()
    print(wifi_connect.ip_address())
    print(wifi.radio.hostname)
    print(customize.datetime.ntpSync())
except:
    pass

