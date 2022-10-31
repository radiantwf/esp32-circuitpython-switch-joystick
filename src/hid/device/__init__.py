from hid.device import device, hori, switch_pro
Device_HORIPAD_S = hori.Tag
Device_Switch_Pro = switch_pro.Tag

def get_device(tag)-> device.Device:
	if tag == Device_HORIPAD_S:
		return hori.Device_Horipad_S()
	elif tag == Device_Switch_Pro:
		return switch_pro.Device_Switch_Pro()
	else:
		return switch_pro.Device_Switch_Pro()
