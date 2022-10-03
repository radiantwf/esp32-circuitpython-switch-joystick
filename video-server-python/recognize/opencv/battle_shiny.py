import multiprocessing
import cv2
import time
import asyncio
import numpy as np
from recognize import frame
from PIL import ImageDraw, ImageFont,Image
import datatype.device as device
import controller.send_order as send_order
import controller.macro as macro

from recognize.opencv.opencv import OpenCV

class BattleShiny(OpenCV):
    def __init__(self,frame:frame.Frame):
        super().__init__(frame)
        self._template = None
        self._fontText = ImageFont.truetype('resources/font/simsun.ttc', 32, encoding="utf-8")
        self._template = cv2.imread("resources/img/battle_shiny.jpg")
        self._template = cv2.cvtColor(self._template, cv2.COLOR_BGR2GRAY)
        self._template_p = (865,430)
    
    async def run(self,opencv_processed_video_frame:multiprocessing.Queue,dev_joystick:device.JoystickDevice):
        order =  send_order.OrderSender(dev_joystick)
        await asyncio.sleep(5)
        last_span_frame_count = 0
        span_second = 0
        _start_monotonic = time.monotonic()
        _frame_count = 0
        order.enable(True)
        await order.add_order(macro.macro_close_game)
        await asyncio.sleep(1)
        await order.add_order(macro.macro_press_button_a_loop)
        macro_run = True
        while True:
            if time.monotonic() - _start_monotonic > 60 and order.enabled:
                await order.add_order(macro.macro_close_game)
                await asyncio.sleep(1)
                await order.add_order(macro.macro_press_button_a_loop)
                _start_monotonic = time.monotonic()
                macro_run = True
                _frame_count = 0

            data = await self._frame.get_frame()
            image = (
                np
                .frombuffer(data, np.uint8)
                .reshape([self._frame.height, self._frame.width, 3])
            )
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            match = cv2.matchTemplate(gray, self._template, cv2.TM_CCOEFF_NORMED)
            _,max_val,_,p=cv2.minMaxLoc(match)
            if max_val > 0.75 and abs(p[0] - self._template_p[0])<=10 and abs(p[1] - self._template_p[1])<=10:
                if macro_run:
                    await order.add_order(macro.macro_action_clear)
                    macro_run = False
                if time.monotonic() - _start_monotonic > 0.15 and _frame_count>0:
                    last_span_frame_count = _frame_count
                    span_second = time.monotonic() - _start_monotonic
                _frame_count=0
                _start_monotonic = time.monotonic()
                x = p[0] +  self._template.shape[0] - 1
                y = p[1] +  self._template.shape[1] - 1
                if y >= self._frame.height:
                    x = self._frame.height - 1
                if y >= self._frame.width:
                    x = self._frame.width - 1
                image = cv2.rectangle(image, p, (x,y), (0, 255, 0), 4, 4)
            else:
                _frame_count += 1
            
            if span_second < 3 and span_second > 0.15 and last_span_frame_count > 0:
                img = Image.fromarray(image)
                draw = ImageDraw.Draw(img)
                draw.text((40, 50), "间隔时间：{:.3f}秒".format(span_second), (0, 255, 0), font=self._fontText)
                draw.text((40, 82), "{:d}帧".format(last_span_frame_count), (0, 255, 0), font=self._fontText)
                image = np.asarray(img)
            try:
                opencv_processed_video_frame.put(image.tobytes(),False,0)
            except:
                pass

            if span_second < 2 and span_second > 0.15 and last_span_frame_count > 0 and not macro_run:
                if span_second < 0.7:
                    await order.add_order(macro.macro_close_game)
                    await asyncio.sleep(1)
                    await order.add_order(macro.macro_press_button_a_loop)
                    macro_run = True
                else:
                    await order.add_order(macro.macro_action_clear)
                    macro_run = False
                    order.enable(False)
