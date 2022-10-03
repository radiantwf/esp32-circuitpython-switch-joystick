import asyncio
import datatype.device as device
import controller.macro

class OrderSender(object):
    def __init__(self,dev:device.JoystickDevice):
        self._enable = True
        self._queue = asyncio.Queue(100)
        asyncio.create_task(self.loop_run(dev))

    async def loop_run(self,dev):
        while True:
            reader,writer = await asyncio.open_connection(dev.host,dev.port)
            while True:
                try:
                    await asyncio.sleep(0.2)
                    macro = None
                    try:
                        macro = self._queue.get_nowait()
                    except:
                        pass
                    try:
                        while True:
                            await asyncio.wait_for(reader.read(1024),0)
                    except asyncio.TimeoutError:
                        pass
                    if macro == None:
                        continue
                    if self._enable:
                        writer.write(macro.message)
                        await writer.drain()
                except Exception as e:
                    print(e)
                    break
    
    async def add_order(self,m:controller.macro):
        await self._queue.put(m)

    def enable(self,e):
        self._enable=e

    @property
    def enabled(self):
        return self._enable