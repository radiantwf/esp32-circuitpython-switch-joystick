import asyncio
from io import BytesIO
import datatype.device as device

class OrderSender(object):
    def __init__(self,dev:device.JoystickDevice):
        self._queue = asyncio.Queue(100)
        self._queue_output = asyncio.Queue(100)

    async def loop_run(self,dev):
        while True:
            try:
                reader,writer = await asyncio.open_connection(dev.host,dev.port)
                while True:
                    try:
                        await asyncio.sleep(0.2)
                        action = None
                        try:
                            action = self._queue.get_nowait()
                        except:
                            pass
                        bytes = BytesIO()
                        try:
                            while True:
                                ret = await asyncio.wait_for(reader.read(1024),timeout=0.001)
                                bytes.write(ret)
                        except asyncio.TimeoutError:
                            pass
                        bytes.flush()
                        bytes.seek(0)
                        lines = bytes.readlines()
                        if len(lines) > 0:
                            for line in lines:
                                line = line.decode("utf-8").strip()
                                if line == "" or line=="ping":
                                    continue
                                if self._queue_output.full():
                                    self._queue_output.get_nowait()
                                self._queue_output.put_nowait(line)
                        bytes.close()

                        if action == None:
                            continue
                        writer.write(action)
                        await writer.drain()
                    except Exception as e:
                        print(e)
                        break
            except Exception as e:
                print(e)
    
    async def add_order(self,action:str):
        await self._queue.put(action)

    async def loop_outputs(self,func):
        while True:
            data = await self._queue_output.get()
            if func != None:
                await func("控制器：" + data)
