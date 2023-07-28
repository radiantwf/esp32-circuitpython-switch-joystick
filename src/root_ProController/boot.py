import hid.device

device = hid.device.get_device(hid.device.Device_Switch_Pro)
device.init_device()