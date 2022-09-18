import time
from adafruit_hid import find_device
import asyncio

_Input0_Y = 0b1
_Input0_B = 0b10
_Input0_A = 0b100
_Input0_X = 0b1000
_Input0_L = 0b10000
_Input0_R = 0b100000
_Input0_ZL = 0b1000000
_Input0_ZR = 0b10000000

_Input1_Minus = 0b1
_Input1_Plus = 0b10
_Input1_LPress = 0b100
_Input1_RPress = 0b1000
_Input1_Home = 0b10000
_Input1_Capture = 0b100000

_Input2_DPadTop = 0
_Input2_DPadTopRight = 1
_Input2_DPadRight = 2
_Input2_DPadBottomRight = 3
_Input2_DPadBottom = 4
_Input2_DPadBottomLeft = 5
_Input2_DPadLeft = 6
_Input2_DPadTopLeft = 7
_Input2_DPadCenter = 8


class JoyStickInput:
    def __init__(self, input_line):
        self._buffer = bytearray(8)
        self._buffer[2] = _Input2_DPadCenter
        self._buffer[3] = 128
        self._buffer[4] = 128
        self._buffer[5] = 128
        self._buffer[6] = 128

        splits = input_line.upper().split("|", -1)
        for s in splits:
            s = s.strip()
            if s == "Y":
                self._buffer[0] |= _Input0_Y
            elif s == "B":
                self._buffer[0] |= _Input0_B
            elif s == "X":
                self._buffer[0] |= _Input0_X
            elif s == "A":
                self._buffer[0] |= _Input0_A
            elif s == "L":
                self._buffer[0] |= _Input0_L
            elif s == "R":
                self._buffer[0] |= _Input0_R
            elif s == "ZL":
                self._buffer[0] |= _Input0_ZL
            elif s == "ZR":
                self._buffer[0] |= _Input0_ZR
            elif s == "MINUS":
                self._buffer[1] |= _Input1_Minus
            elif s == "PLUS":
                self._buffer[1] |= _Input1_Plus
            elif s == "LPRESS":
                self._buffer[1] |= _Input1_LPress
            elif s == "RPRESS":
                self._buffer[1] |= _Input1_RPress
            elif s == "HOME":
                self._buffer[1] |= _Input1_Home
            elif s == "CAPTURE":
                self._buffer[1] |= _Input1_Capture
            elif s == "CENTER":
                self._buffer[2] = _Input2_DPadCenter
            elif s == "TOP":
                if self._buffer[2] != _Input2_DPadCenter:
                    self._buffer[2] = _Input2_DPadCenter
                else:
                    self._buffer[2] = _Input2_DPadTop
            elif s == "TOPRIGHT":
                if self._buffer[2] != _Input2_DPadCenter:
                    self._buffer[2] = _Input2_DPadCenter
                else:
                    self._buffer[2] = _Input2_DPadTopRight
            elif s == "RIGHT":
                if self._buffer[2] != _Input2_DPadCenter:
                    self._buffer[2] = _Input2_DPadCenter
                else:
                    self._buffer[2] = _Input2_DPadRight
            elif s == "BOTTOMRIGHT":
                if self._buffer[2] != _Input2_DPadCenter:
                    self._buffer[2] = _Input2_DPadCenter
                else:
                    self._buffer[2] = _Input2_DPadBottomRight
            elif s == "BOTTOM":
                if self._buffer[2] != _Input2_DPadCenter:
                    self._buffer[2] = _Input2_DPadCenter
                else:
                    self._buffer[2] = _Input2_DPadBottom
            elif s == "BOTTOMLEFT":
                if self._buffer[2] != _Input2_DPadCenter:
                    self._buffer[2] = _Input2_DPadCenter
                else:
                    self._buffer[2] = _Input2_DPadBottomLeft
            elif s == "LEFT":
                if self._buffer[2] != _Input2_DPadCenter:
                    self._buffer[2] = _Input2_DPadCenter
                else:
                    self._buffer[2] = _Input2_DPadLeft
            elif s == "TOPLEFT":
                if self._buffer[2] != _Input2_DPadCenter:
                    self._buffer[2] = _Input2_DPadCenter
                else:
                    self._buffer[2] = _Input2_DPadTopLeft
            else:
                stick = s.split("@", -1)
                if len(stick) == 2:
                    x = 0
                    y = 0
                    coordinate = stick[1].split(",", -1)
                    if len(coordinate) == 2:
                        x = self._coordinate_str_convert_int(coordinate[0])
                        y = self._coordinate_str_convert_int(coordinate[1])
                    x += 128
                    y += 128
                    if stick[0] == "LSTICK":
                        if self._buffer[3] == 128 and self._buffer[4] == 128:
                            self._buffer[3] = x
                            self._buffer[4] = y
                    elif stick[0] == "RSTICK":
                        if self._buffer[5] == 128 and self._buffer[6] == 128:
                            self._buffer[5] = x
                            self._buffer[6] = y

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


class JoyStick:
    def __init__(self, devices):
        self._joystick_device = find_device(
            devices, usage_page=0x1, usage=0x05)
        try:
            self.release()
        except OSError:
            time.sleep(1)
            self.release()

    def _send(self,  input_line: str = ""):
        input = JoyStickInput(input_line)
        self._joystick_device.send_report(input.buffer())

    def release(self):
        self._send("")

    async def key_press(self,  input_line: str = "", keep: float = 0.01):
        if keep < 0:
            keep = 0.01
        while keep > 1:
            self._send(input_line)
            await asyncio.sleep(1)
            keep -= 1
        self._send(input_line)
        await asyncio.sleep(keep)
        self.release()

    async def do_action(self,  action_line: str = ""):
        splits = action_line.split(":")
        if len(splits) > 2:
            self.release()
            return
        if len(splits) == 1:
            try:
                keep = float(splits[0])
                await self.key_press("", keep)
            except:
                await self.key_press(splits[0], 0.1)
        else:
            keep = 0.1
            try:
                keep = float(splits[1])
            except:
                pass
            await self.key_press(splits[0], keep)
