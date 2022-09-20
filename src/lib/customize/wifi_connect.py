from . import config
import wifi
import time

_config = config.Config()
_ssid = _config.get("ssid", "wifi")
_pwd = _config.get("pwd", "wifi")
_wifi_type = _config.get("type", "wifi")
print(_wifi_type)
print(_ssid)
print(_pwd)


def connect():
    if _wifi_type == "ap":
        wifi.radio.start_ap(_ssid, _pwd)
    else:
        wifi.radio.connect(_ssid, _pwd)


def disconnect():
    try:
        if _wifi_type == "ap":
            wifi.radio.stop_ap()
        else:
            wifi.radio.stop_station()
    except:
        pass

def ip_address():
    if _wifi_type == 'ap':
        return wifi.radio.ipv4_address_ap
    return wifi.radio.ipv4_address