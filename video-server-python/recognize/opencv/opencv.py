import asyncio
import multiprocessing
import socket
from controller.macro import Macro
from recognize import frame

class OpenCV(object):
    def __init__(self,frame:frame.Frame,opencv_processed_video_frame:multiprocessing.Queue,controller_action_queue:multiprocessing.Queue,log_udp_port = 41001):
        self._frame = frame
        self._opencv_processed_video_frame = opencv_processed_video_frame
        self._controller_action_queue = controller_action_queue
        self._log_udp_port = log_udp_port
        self._enable_send_action = True

    
    def send_log(self,msg):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(msg.encode("utf-8"), ("127.0.0.1", self._log_udp_port)) 
    

    async def send_action(self,m:Macro,timeout:float = None):
        try:
            await asyncio.wait_for(self._send_action(m),timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def _send_action(self,m:Macro):
        if not self._enable_send_action:
            return
        while True:
            try:
                self._controller_action_queue.put_nowait(m)
            except:
                await asyncio.sleep(0.1)
            return
    
