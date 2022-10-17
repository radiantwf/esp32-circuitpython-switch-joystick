import usb_hid
import hid.device.switch_pro
import customize.wifi_connect as wifi_connect
import customize.datetime
import wifi

usb_hid.enable((hid.device.switch_pro.SwitchPro,))
wifi_connect.connect()
print(wifi_connect.ip_address())
print(wifi.radio.hostname)
print(customize.datetime.ntpSync())
