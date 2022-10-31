class JoyStick:
    pass

    async def start(self):
        pass

    def start_realtime(self):
        pass

    def stop_realtime(self):
        pass

    async def send_realtime_action(self,action:str):
        pass

    async def release(self,release_monotonic_ns:float = 0):
        pass

    async def do_action(self,action_line: str = ""):
        pass
