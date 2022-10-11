import hid.device.hori
import hid.device.switch_pro
from hid.joystick.hori import JoyStick_HORI_S
from hid.joystick.pro_controller import JoyStick_PRO_CONTROLLER

class JoyStickFactory:
    _instance = None
    @staticmethod
    def get_instance(tag:str = ""):
        if JoyStickFactory._instance == None:
            if tag == hid.device.hori.Tag:
                JoyStickFactory._instance = JoyStick_HORI_S()
            elif tag == hid.device.switch_pro.Tag:
                JoyStickFactory._instance = JoyStick_PRO_CONTROLLER()
            else:
                JoyStickFactory._instance = JoyStick_HORI_S()
        return JoyStickFactory._instance