from macros import action
import hid.joystick
import asyncio
import usb_hid
import customize.config as config
import customize.task_manager as task_manager
import customize.udp_server as udp_server

joystick = hid.joystick.JoyStick(usb_hid.devices)

TASK_TAG: str = "macros"
_running: bool = False


async def auto_run():
    c = config.Config()
    name = c.get("autorun.name", "macros")
    try:
        loop = c.get("autorun.loop", "macros")
    except:
        loop = 1
    await create_task(name, loop)


async def create_task(name: str, loop: int = 1):
    c = config.Config()
    key = c.get("macros.{}".format(name), "command")
    if key == None:
        key = name
    tm = task_manager.TaskManager()
    tm.create_task(_run(key, loop), TASK_TAG)


async def stop():
    global _running
    _running = False
    tm = task_manager.TaskManager()
    await tm.cancel_task(TASK_TAG)


async def _run(name: str, loop: int = 1):
    udp = udp_server.UdpServer()
    msg = "开始运行{}脚本，循环次数：{}".format(name, loop)
    udp.broadcast_message(msg)
    print(msg)
    times = 0
    global _running
    try:
        act = _get_action(name)
        if act == None:
            return
        _running = True
        while True:
            while True:
                if not _running:
                    raise asyncio.CancelledError
                ret = act.pop()
                # print(ret[0])
                await joystick.do_action(ret[0])
                if ret[1]:
                    break
            times += 1
            if loop > 0 and times >= loop:
                break
            act.cycle_reset()
        msg = "脚本{}运行完成，当前运行次数：{}".format(name, times)
        udp.broadcast_message(msg)
        print(msg)
    except asyncio.CancelledError:
        joystick.release()
        msg = "脚本{}运行中止，当前运行次数：{}".format(name, times)
        udp.broadcast_message(msg)
        print(msg)
    finally:
        _running = False


def _get_action(name: str) -> action.Action:
    act = action.Action(name)
    if act._head == None:
        return None
    return act
