import asyncio
import multiprocessing
import time

class Frame(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Frame, cls).__new__(cls)
        return cls._instance

    _first = True

    def __init__(self,width = 960,height = 540,fps = 5):
        if Frame._first:
            Frame._first = False
            self._queue = asyncio.Queue(1)
            self._raw = None
            self._width = width
            self._height = height
            self._fps = fps
            self._last_set_frame_monotonic_ns = time.monotonic_ns()

    def set_frame_nowait(self,data)->bool:
        if time.monotonic_ns() - self._last_set_frame_monotonic_ns < 1000000000/self._fps:
            return False
        if not self._queue.empty():
            self._queue.get_nowait()
        try:
            self._queue.put_nowait(data)
            self._last_set_frame_monotonic_ns = time.monotonic_ns()
            return True
        except asyncio.QueueFull:
            return False

    async def get_frame(self):
        return await self._queue.get()

    def get_frame_nowait(self):
        try:
            return self._queue.get_nowait()
        except asyncio.QueueEmpty:
            return None
    
    async def loop_read(self,process_queue:multiprocessing.Queue):
        data = None
        while True:
            try:
                while True:
                    _data = process_queue.get_nowait()
                    data = _data
            except:
                pass
            if data == None:
                await asyncio.sleep(0.01)
                continue
            if self.set_frame_nowait(data):
                data == None
            await asyncio.sleep(0.01)
    @property
    def width(self):
        return self._width
    @property
    def height(self):
        return self._height