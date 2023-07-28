import asyncio


class TaskManager(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(TaskManager, cls).__new__(cls)
        return cls._instance

    _first = True

    def __init__(self):
        if TaskManager._first:
            TaskManager._first = False
            self._loop = asyncio.get_event_loop()
            self._dic_tasks = dict()

    def wait_forever(self):
        self._loop.run_forever()

    def create_task(self, coro, key=None):
        if key == None:
            self._loop.create_task(coro)
            return
        if self._dic_tasks.get(key) == None:
            task = self._loop.create_task(coro)
            self._dic_tasks[key] = task
            self._loop.create_task(self.wait_task(task, key))

    def close_loop(self):
        self._loop.close()

    async def wait_task(self, task, key):
        try:
            await task
            print("{}任务完成".format(key))
        except Exception as e:
            print(e)
        self._dic_tasks.pop(key)

    async def cancel_task(self, key: str):
        task = self._dic_tasks.get(key)
        if task == None:
            return
        task.cancel()
        await task
