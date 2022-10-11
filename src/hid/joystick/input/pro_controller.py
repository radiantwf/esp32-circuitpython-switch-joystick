from hid.joystick.input.joystick_input import JoyStickInput


class JoyStickInput_PRO_CONTROLLER(JoyStickInput):
    def __init__(self, input_line):
        self._buffer = bytearray(8)

    def buffer(self):
        return self._buffer