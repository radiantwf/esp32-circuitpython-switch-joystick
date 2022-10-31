import hid.device
from hid.joystick.hori import JoyStick_HORI_S
from hid.joystick.pro_controller import JoyStick_PRO_CONTROLLER

class JoyStickFactory:
    _instance = None
    @staticmethod
    def get_instance(tag:str = ""):
        if JoyStickFactory._instance == None:
            if tag == hid.device.Device_HORIPAD_S:
                JoyStickFactory._instance = JoyStick_HORI_S()
            elif tag == hid.device.Device_Switch_Pro:
                JoyStickFactory._instance = JoyStick_PRO_CONTROLLER()
            else:
                JoyStickFactory._instance = JoyStick_PRO_CONTROLLER()
        return JoyStickFactory._instance