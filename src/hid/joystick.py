import time
from adafruit_hid import find_device
from hid import joystick_input
import asyncio


_Mini_Key_Send_Span_ns = 3000000

class JoyStick:
    def __init__(self, devices):
        self._joystick_device = find_device(
            devices, usage_page=0x1, usage=0x05)
        self._last_send_monotonic_ns = 0
        try:
            self._sync_release()
        except OSError:
            time.sleep(1)
            self._sync_release()

    def _sync_release(self):
        self._sync_send(joystick_input.JoyStickInput(""))

    def _sync_send(self,input:joystick_input.JoyStickInput):
        self._joystick_device.send_report(input.buffer())
        self._last_send_monotonic_ns = time.monotonic_ns()


    async def _send(self,  input_line: str = "",earliest_send_key_monotonic_ns=0):
        earliest = self._last_send_monotonic_ns + _Mini_Key_Send_Span_ns
        if earliest < earliest_send_key_monotonic_ns:
            earliest = earliest_send_key_monotonic_ns
        input = joystick_input.JoyStickInput(input_line)
        while True:
            now = time.monotonic_ns()
            if now < earliest:
                ms = int((earliest - now)/1000000)
                await asyncio.sleep_ms(ms)
                break
            else:
                break
        # print((time.monotonic_ns() - earliest)/1000000)
        self._sync_send(input)

    async def release(self,release_monotonic_ns:float = 0):
        await self._send("",release_monotonic_ns)

    async def key_press(self,  input_line: str = "", keep: float = 0.005):
        await self._send(input_line,0)
        release_monotonic_ns = self._last_send_monotonic_ns + keep*1000000000
        await self.release(release_monotonic_ns)

    async def do_action(self,  action_line: str = ""):
        print(action_line)
        splits = action_line.split(":")
        if len(splits) > 2:
            await self.release()
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
