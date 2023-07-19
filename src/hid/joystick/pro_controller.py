from hid.joystick.input.pro_controller import JoyStickInput_PRO_CONTROLLER
from hid.joystick.joystick import JoyStick
import hid.device
import time
import asyncio
_Min_Key_Send_Span_ns = 3 * 1000000
_Key_Send_Loop_Span_ms = 1
_Send_Bytes_Length = 63
_Space_Buffer = bytearray(_Send_Bytes_Length)

mac_addr = b'\x00\x00\x5e\x00\x53\x5e'
serial_number = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'

class JoyStick_PRO_CONTROLLER(JoyStick):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(JoyStick_PRO_CONTROLLER, cls).__new__(cls)
        return cls._instance

    _first = True

    def __init__(self):
        if JoyStick_PRO_CONTROLLER._first:
            JoyStick_PRO_CONTROLLER._first = False
            self._start_ns = time.monotonic_ns()
            self._action_lock = asyncio.Lock()
            self._action_line = ""
            self._last_key_press_ns = 0
            device = hid.device.get_device(hid.device.Device_Switch_Pro)
            self._joystick_device = device.find_device()

    def _get_counter(self):
        return int((time.monotonic_ns() - self._start_ns) * 360 / 1000000000 ) & 0xff
    
    async def _send_loop(self):
        while True:
            await asyncio.sleep_ms(_Key_Send_Loop_Span_ms)
            if not self._connected:
                continue
            action_line = ""
            async with self._action_lock:
                action_line = self._action_line
            input = JoyStickInput_PRO_CONTROLLER(action_line)
            self._send_counter_data(input.buffer(),0x30)

    async def _recv_0x80(self):
        while True:
            buffer = None
            while True:
                buf = self._recv_data(0x80)
                if not buf:
                    break
                buffer = buf
            if buffer:
                cmd = buffer[0]
                if cmd == 0x01:
                    b = bytearray([cmd])
                    b.extend(bytearray(b'\x00\x03'))
                    b.extend(bytearray(mac_addr))
                    self._send_data(b,0x81)
                elif cmd == 0x02 or cmd == 0x03:
                    b = bytearray([cmd])
                    self._send_data(b,0x81)
                elif cmd == 0x04:
                    print("连接手柄")
                    self._connected = True
                elif cmd == 0x05:
                    print("断开手柄")
                    self._connected = False
            else:
                pass
            await asyncio.sleep_ms(10)

    async def _recv_0x01(self):
        while True:
            buffer = None
            while True:
                buf = self._recv_data(0x01)
                if not buf:
                    break
                buffer = buf
            if buffer:
                subcmd = buffer[9]
                if subcmd == 0x01: # Bluetooth manual pairing
                    await self._uart_response(0x81, subcmd, [0x03])
                # REQUEST_DEVICE_INFO 0x02
                elif subcmd == 0x02: # Request device info
                    # 0-1 Firmware version (Eg: 3.139)
                    # 2 Controller ID (1 = Joy-Con (L), 2 = Joy-Con (R), 3 = Pro Controller)
                    # 3 Unknown, always 02 (maybe?)
                    # 4-9 Controller Bluetooth MAC address
                    # 10 Unknown, always 01 (maybe?)
                    # 11 If 01, colors in SPI used for Controller color
                    b = bytearray(b'\x04\x21\x03\x02')
                    b.extend(bytearray(mac_addr))
                    b.extend(bytearray(b'\x01\x01'))
                    await self._uart_response(0x82, subcmd, b)
                # SET_MODE 0x03
                # SET_SHIPMENT 0x08
                # SET_PLAYER 0x30
                # TOGGLE_IMU 0x40
                # ENABLE_VIBRATION 0x48
                # 0x38 ?
                elif subcmd == 0x03 or subcmd == 0x33 or subcmd == 0x08 or subcmd == 0x30 or subcmd == 0x38 or subcmd == 0x40 or subcmd == 0x41 or subcmd == 0x48:
                    await self._uart_response(0x80, subcmd, [])
                # TRIGGER_BUTTONS 0x04
                elif subcmd == 0x04: # Trigger buttons elapsed time
                    await self._uart_response(0x83, subcmd, [])
                # SET_NFC_IR_CONFIG 0x21
                elif subcmd == 0x21: # Set NFC/IR MCU configuration
                    await self._uart_response(0xa0, subcmd, bytearray(b'\x01\x00\xff\x00\x08\x00\x1B\x01'))
                # SET_NFC_IR_STATE 0x22
                elif subcmd == 0x22:
                    await self._uart_response(0x80, subcmd, [])
                # SPI_READ 0x10
                elif subcmd == 0x10:
                    if buffer[10:12] == b'\x00\x60': # Serial number
                        await self._spi_response(buffer[10:12], bytearray(serial_number))
                    elif buffer[10:12] == b'\x50\x60': # Controller Color
                        # 1-3 Body RGB Color
                        # 4-6 Buttons RGB Color
                        # 7-9 Pro Controller Left Grip RGB Color
                        # 10-12 Pro Controller Right Grip RGB Color
                        await self._spi_response(buffer[10:12], bytearray(b'\xbc\x11\x42\x75\xa9\x28\xff\xff\xff\xff\xff\xff'))
                    elif buffer[10:12] == b'\x3d\x60': # Factory configuration & calibration 2
                        # 1-18 Stick factory calibration
                        # 19 always 0xFF
                        # 20-25 Controller Colors
                        # await self._spi_response(buffer[10:12], bytearray(b'\xba\x15\x62\x11\xb8\x7f\x29\x06\x5b\xff\xe7\x7e\x0e\x36\x56\x9e\x85\x60\xff\x82\x82\x82\x0f\x0f\x0f'))
                        await self._spi_response(buffer[10:12], bytearray(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'))
                    elif buffer[10:12] == b'\x10\x80': # User Analog Sticks calibration
                        # Since there's no user calibration information, the Joy-Con responds with 24 bytes of 0xFF. 
                        # The Switch determines if there's user calibration if 0x8010-0x8011 equals 0xB2 0xA1 (start of left stick data) and 0x801B-0x801C equals 0xB2 0xA1.
                        await self._spi_response(buffer[10:12], bytearray(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'))
                    elif buffer[10:12] == b'\x98\x60': # Factory Stick device parameters 2
                        # Joy-Con replies with the 18 bytes read from SPI Memory 0x6098-0x60A9.
                        # The factory stick device parameters stored are the same (almost always) as the stick parameters stored at 0x6086-0x6097. Check the above section for info on this read.
                        # await self._spi_response(buffer[10:12], bytearray(b'\x12\x19\xD0\x4C\xAE\x40\xE1\xEE\xE2\x2E\xEE\xE2\x2E\xB4\x4A\xAB\x96\x64\x49'))
                        await self._spi_response(buffer[10:12], bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'))
                    elif buffer[10:12] == b'\x80\x60': # Factory Sensor and Stick device parameters
                        # 1-2 Six-Axis Horizontal Offsets Axis-X
                        # 3-4 Six-Axis Horizontal Offsets Axis-Y
                        # 5-6 Six-Axis Horizontal Offsets Axis-Z
                        await self._spi_response(buffer[10:12], bytearray(b'\x50\xFD\x00\x00\xC6\x0F'))
                    elif buffer[10:12] == b'\x86\x60': # Factory Sensor and Stick device parameters
                        # 1-18  Define min/max range and dead zone for the sticks. These values are the same for all controllers.
                        await self._spi_response(buffer[10:12], bytearray(b'\x00\x40\x00\x40\x00\x40\xFA\xFF\xD0\xFF\xC7\xFF\x3B\x34\x3B\x34\x3B\x34'))
                    elif buffer[10:12] == b'\x20\x60': # User 6-Axis Motion Sensor calibration
                        # 1-6 Acceleration origin position (Joy-Con on table, face-up)
                        # 7-12 Acceleration sensitivity coefficient
                        # 13-18 Gyro origin when still
                        # 19-24 Gyro sensitivity coefficient
                        await self._spi_response(buffer[10:12], bytearray(b'\x09\x01\x18\xFF\xED\xFF\x00\x40\x00\x40\x00\x40\xFA\xFF\xD0\xFF\xC7\xFF\x3B\x34\x3B\x34\x3B\x34'))
                        # await self._spi_response(buffer[10:12], bytearray(b'\xD3\xFF\xD5\xFF\x55\x01\x00\x40\x00\x40\x00\x40\x19\x00\xDD\xFF\xDC\xFF\x3B\x34\x3B\x34\x3B\x34'))
                    # elif buffer[10:12] == b'\x28\x80': # User 6-Axis Motion Sensor calibration
                    #     await self._spi_response(buffer[10:12], bytearray(b'\xbe\xff\x3e\x00\xf0\x01\x00\x40\x00\x40\x00\x40\xfe\xff\xfe\xff\x08\x00\xe7\x3b\xe7\x3b\xe7\x3b'))
            else:
                pass
            await asyncio.sleep_ms(5)

    async def _uart_response(self, code, subcmd, data):
        action_line = ""
        async with self._action_lock:
            action_line = self._action_line
        input = JoyStickInput_PRO_CONTROLLER(action_line)
        buf = bytearray(input.buffer())
        buf.extend(bytearray([code, subcmd]))
        buf.extend(bytearray(data))
        self._send_counter_data(buf,0x21)

    async def _spi_response(self, addr, data):
        buf = bytearray(addr)
        buf.extend(bytearray([0x00, 0x00]))
        buf.append(len(data))
        buf.extend(bytearray(data))
        await self._uart_response(0x90, 0x10, buf)
    
    def _recv_data(self,report_id):
        buffer = self._joystick_device.get_last_received_report(report_id)
        return buffer

    def _send_data(self,data:bytearray,report_id):
        buffer = bytearray()
        if data and len(data) >= _Send_Bytes_Length:
            buffer.extend(data[:_Send_Bytes_Length])
        else:
            buffer.extend(data)
            buffer.extend(_Space_Buffer[len(data):])
        self._joystick_device.send_report(buffer,report_id)

    def _send_counter_data(self,data:bytearray,report_id):
        buffer = bytearray([self._get_counter()])
        if data and len(data) + 1 >= _Send_Bytes_Length:
            buffer.extend(data[:_Send_Bytes_Length - 1])
        else:
            buffer.extend(data)
            buffer.extend(_Space_Buffer[len(buffer):])
        self._joystick_device.send_report(buffer,report_id)

    async def start(self):
        self._start_ns = time.monotonic_ns()
        self._connected = False
        asyncio.create_task(self._send_loop())
        asyncio.create_task(self._recv_0x80())
        asyncio.create_task(self._recv_0x01())

    def start_realtime(self):
        pass

    def stop_realtime(self):
        pass

    async def send_realtime_action(self,action_line):
        async with self._action_lock:
            if self._action_line != action_line:
                self._action_line = action_line
        self._last_key_press_ns = time.monotonic_ns()

    async def _send(self,  input_line: str = "",earliest_send_key_monotonic_ns=0):
        earliest = self._last_key_press_ns + _Min_Key_Send_Span_ns
        if earliest < earliest_send_key_monotonic_ns:
            earliest = earliest_send_key_monotonic_ns
        loop = 0
        while True:
            loop += 1
            now = time.monotonic_ns()
            if now >= earliest:
                break
            elif now < earliest - _Min_Key_Send_Span_ns:
                ms = int((earliest - now  - _Min_Key_Send_Span_ns)/1000000)
                await asyncio.sleep_ms(ms)
            else:
                time.sleep(0.0001)
        t1 = time.monotonic_ns()
        await self.send_realtime_action(input_line)
        t2 = time.monotonic_ns()

    async def _key_press(self,  inputs = []):
        release_monotonic_ns = 0
        last_action = ""
        for input_line in inputs:
            last_action = input_line[0]
            if input_line[0] == "~":
                continue
            await self._send(input_line[0],release_monotonic_ns)
            release_monotonic_ns = self._last_key_press_ns + input_line[1]*1000000000
        if last_action != "~":
            await self.release(release_monotonic_ns)

    async def release(self,release_monotonic_ns:float = 0):
        await self._send("",release_monotonic_ns)

    async def do_action(self,  action_line: str = ""):
        inputs = []
        actions = action_line.split("->")
        for action in actions:
            splits = action.split(":")
            if len(splits) > 2:
                continue
            p1 = splits[0]
            p2 = 0.1
            if len(splits) == 1:
                try:
                    p2 = float(splits[0])
                    p1 = ""
                except:
                    pass
            else:
                try:
                    p2 = float(splits[1])
                except:
                    pass
            inputs.append((p1,p2))
        await self._key_press(inputs)