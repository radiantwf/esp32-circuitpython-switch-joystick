from hid.joystick.input.joystick_input import JoyStickInput

_Input0_Y = 0b1
_Input0_X = 0b10
_Input0_B = 0b100
_Input0_A = 0b1000
_Input0_JCL_SR = 0b10000
_Input0_JCL_SL = 0b100000
_Input0_R = 0b1000000
_Input0_ZR = 0b10000000

_Input1_Minus = 0b1
_Input1_Plus = 0b10
_Input1_RPress = 0b100
_Input1_LPress = 0b1000
_Input1_Home = 0b10000
_Input1_Capture = 0b100000

_Input2_Bottom = 0b1
_Input2_Top = 0b10
_Input2_Right = 0b100
_Input2_Left = 0b1000
_Input2_JCR_SR = 0b10000
_Input2_JCR_SL = 0b100000
_Input2_L = 0b1000000
_Input2_ZL = 0b10000000

class JoyStickInput_PRO_CONTROLLER(JoyStickInput):

    def __init__(self, input_line):
        self._buffer = bytearray(11)
        self._buffer[0] =0x81
        self._buffer[10] =0x00
        lx = 0x800
        ly = 0x800
        rx = 0x800
        ry = 0x800

        splits = input_line.upper().split("|", -1)
        for s in splits:
            s = s.strip()
            if s == "Y":
                self._buffer[1] |= _Input0_Y
            elif s == "X":
                self._buffer[1] |= _Input0_X
            elif s == "B":
                self._buffer[1] |= _Input0_B
            elif s == "A":
                self._buffer[1] |= _Input0_A
            elif s == "JCL_SR":
                self._buffer[1] |= _Input0_JCL_SR
            elif s == "JCL_SL":
                self._buffer[1] |= _Input0_JCL_SL
            elif s == "R":
                self._buffer[1] |= _Input0_R
            elif s == "ZR":
                self._buffer[1] |= _Input0_ZR
        
            elif s == "MINUS":
                self._buffer[2] |= _Input1_Minus
            elif s == "PLUS":
                self._buffer[2] |= _Input1_Plus
            elif s == "LPRESS":
                self._buffer[2] |= _Input1_LPress
            elif s == "RPRESS":
                self._buffer[2] |= _Input1_RPress
            elif s == "HOME":
                self._buffer[2] |= _Input1_Home
            elif s == "CAPTURE":
                self._buffer[2] |= _Input1_Capture
                
            elif s == "BOTTOM":
                self._buffer[3] |= _Input2_Bottom
            elif s == "TOP":
                self._buffer[3] |= _Input2_Top
            elif s == "RIGHT":
                self._buffer[3] |= _Input2_Right
            elif s == "LEFT":
                self._buffer[3] |= _Input2_Left
            elif s == "JCR_SR":
                self._buffer[3] |= _Input2_JCR_SR
            elif s == "JCR_SL":
                self._buffer[3] |= _Input2_JCR_SL
            elif s == "L":
                self._buffer[3] |= _Input2_L
            elif s == "ZL":
                self._buffer[3] |= _Input2_ZL
            else:
                stick = s.split("@", -1)
                if len(stick) == 2:
                    x = 0
                    y = 0
                    coordinate = stick[1].split(",", -1)
                    if len(coordinate) == 2:
                        x = self._coordinate_str_convert_int(coordinate[0])
                        y = self._coordinate_str_convert_int(coordinate[1])
                    x = (x + 128) * 16
                    y = (y * (-1) + 128) * 16
                    if x > 0xfff:
                        x = 0xfff
                    if y > 0xfff:
                        y = 0xfff
                    if stick[0] == "LSTICK":
                        lx = x
                        ly = y
                    elif stick[0] == "RSTICK":
                        rx = x
                        ry = y
        self._buffer[4] = lx & 0xff
        self._buffer[5] = ((lx >> 8) & 0x0f) | ((ly & 0x0f) << 4)
        self._buffer[6] = (ly >> 4) & 0xff
        self._buffer[7] = rx & 0xff
        self._buffer[8] = ((rx >> 8) & 0x0f) | ((ry & 0x0f) << 4)
        self._buffer[9] = (ry >> 4) & 0xff

    def _coordinate_str_convert_int(self, str):
        v = 0
        try:
            v = int(float(str))
        except:
            pass
        if v < -128:
            v = -128
        elif v > 127:
            v = 127
        return v

    def buffer(self):
        return self._buffer