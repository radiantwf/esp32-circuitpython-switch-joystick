import usb_hid
import hid.device.hori
import customize.wifi_connect as wifi_connect
import customize.datetime

usb_hid.enable((hid.device.hori.HoriPadS,))
wifi_connect.connect()
print(customize.datetime.ntpSync())
