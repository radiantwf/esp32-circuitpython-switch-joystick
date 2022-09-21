from macros import action
import hid.joystick
import time
import asyncio
import usb_hid
import customize.config as config
import customize.task_manager as task_manager
import customize.udp_server as udp_server

joystick = hid.joystick.JoyStick(usb_hid.devices)

TASK_TAG: str = "macros"
_running: bool = False
_current_info = ""
_result_info = ""
_start_time = None


def status_info():
    global _start_time
    global _result_info
    if _start_time != None and _start_time != 0:
        return current_info()
    elif _result_info != None and _result_info != "":
        return _result_info
    else:
        result_info()


def current_info():
    global _current_info
    global _start_time
    if _start_time == None or _start_time == 0:
        return "没有正在执行的脚本"
    span = int(time.time() - _start_time)
    return _current_info + "持续运行时间：{:.0f}小时{:.0f}分{:.0f}秒".format(span/3600, (span % 3600)/60, span % 60)


def result_info():
    global _result_info
    return _result_info


def auto_run():
    c = config.Config()
    cmd = c.get("autorun", "macros")
    create_task(cmd)


def create_task(cmd: str):
    c = config.Config()
    paras = None
    loop = 1
    splits = cmd.split(":")
    name = splits[0]
    try:
        loop = int(splits[1])
        paras = splits[2:]
    except:
        pass

    key = c.get("macros.{}".format(name), "command")
    if key == None:
        key = name
    tm = task_manager.TaskManager()
    tm.create_task(_run(key, loop, paras), TASK_TAG)
    return "{}：已添加任务。".format((key, loop, paras))


def stop():
    global _running
    _running = False
    # tm = task_manager.TaskManager()
    # await tm.cancel_task(TASK_TAG)


async def _run(name: str, loop: int = 1, paras: list = None):
    udp = udp_server.UdpServer()
    msg = "开始运行{}脚本，循环次数：{}".format(name, loop)
    udp.broadcast_message(msg)
    print(msg)
    times = 0
    if loop <= 0:
        loop = -1
    if paras != None and len(paras) > 0:
        c = config.Config()
        for p in paras:
            v = p.split("=")
            if len(v) == 2:
                c.set_macros_running_setting(v[0], v[1])
    global _running
    global _current_info
    global _result_info
    global _start_time
    start_ts = time.time()
    _start_time = start_ts
    try:
        act = _get_action(name)
        if act == None:
            return
        _running = True
        _result_info = ""
        _current_info = "正在运行[{}]脚本，已运行{}次，计划运行{}次\n".format(
            name, times, loop)
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
            _current_info = "正在运行[{}]脚本，已运行{}次，计划运行{}次\n".format(
                name, times, loop)
            if loop > 0 and times >= loop:
                break
            act.cycle_reset()
        msg = "脚本{}运行完成，当前运行次数：{}".format(name, times)
        udp.broadcast_message(msg)
        print(msg)
        span = time.time() - start_ts
        _result_info = "脚本[{}]运行完成，实际运行{}次\n持续运行时间：{:.0f}小时{:.0f}分{:.0f}秒".format(
            name, times, span/3600, (span % 3600)/60, span % 60)
    except asyncio.CancelledError:
        joystick.release()
        msg = "脚本{}运行中止，当前运行次数：{}".format(name, times)
        udp.broadcast_message(msg)
        print(msg)
        span = time.time() - start_ts
        _result_info = "脚本[{}]运行中断，实际运行{}次，计划运行{}次\n持续运行时间：{:.0f}小时{:.0f}分{:.0f}秒".format(
            name, times, loop, span/3600, (span % 3600)/60, span % 60)
    finally:
        _start_time = None
        _running = False
        _current_info = ""


def _get_action(name: str) -> action.Action:
    act = action.Action(name)
    if act._head == None:
        return None
    return act
