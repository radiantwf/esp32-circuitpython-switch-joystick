import hid.device

device = hid.device.get_device(hid.device.Device_HORIPAD_S)
device.init_device()