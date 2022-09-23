from macros import action,macro
import hid.joystick
import time
import asyncio
import json
import usb_hid
import customize.config as config
import customize.task_manager as task_manager

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
    global _running
    if _start_time == None or _start_time == 0:
        return "没有正在执行的脚本"
    if not _running :
        return "已收到中止指令，正在处理中"
    span = int(time.time() - _start_time)
    return _current_info + "持续运行时间：{:.0f}小时{:.0f}分{:.0f}秒".format(span/3600, (span % 3600)/60, span % 60)


def result_info():
    global _result_info
    return _result_info

def create_task(cmd: str):
    try:
        return _create_task_json(json.loads(cmd))
    except:
        global _result_info
        _result_info = "启动命令{}有错误，请检查。".format(cmd)
        return _result_info


def auto_run():
    c = config.Config()
    try:
        _create_task_json(c.autorun)
    except:
        global _result_info
        _result_info = "Config文件macro.autorun节点存在错误，无法启动脚本"


def _create_task_json(cmd: dict):
    c1 = cmd.get("name")
    c2 = cmd.get("loop")
    paras = cmd.get("paras")
    if type(c1) is str:
        name = c1
    else:
        raise
    
    if type(c2) is int:
        loop = c2
    else:
        loop = -1

    tm = task_manager.TaskManager()
    tm.create_task(_run(name, loop, paras), TASK_TAG)
    return "{}：已添加任务。".format((name, loop, paras))


def stop():
    global _running
    _running = False
    # tm = task_manager.TaskManager()
    # await tm.cancel_task(TASK_TAG)

def published():
    m= macro.Macro()
    if m._publish!= None:
        return json.dumps(m._publish)
    else:
        return ""
    

async def _run(name: str, loop: int = 1, paras: dict = ()):
    msg = "开始运行{}脚本，循环次数：{}".format(name, loop)
    print(msg)
    times = 0
    if loop <= 0:
        loop = -1
    global _running
    global _current_info
    global _result_info
    global _start_time
    start_ts = time.time()
    _start_time = start_ts
    try:
        act = _get_action(name,paras)
        if act == None:
            _result_info = "不存在名称为{}的脚本".format(name)
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
                if ret[0] != None:
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
        print(msg)
        span = time.time() - start_ts
        _result_info = "脚本[{}]运行完成，实际运行{}次\n持续运行时间：{:.0f}小时{:.0f}分{:.0f}秒".format(
            name, times, span/3600, (span % 3600)/60, span % 60)
    except asyncio.CancelledError:
        joystick.release()
        msg = "脚本{}运行中止，当前运行次数：{}".format(name, times)
        print(msg)
        span = time.time() - start_ts
        _result_info = "脚本[{}]停止，实际运行{}次，计划运行{}次\n持续运行时间：{:.0f}小时{:.0f}分{:.0f}秒".format(
            name, times, loop, span/3600, (span % 3600)/60, span % 60)
    finally:
        _start_time = None
        _running = False
        _current_info = ""


def _get_action(name: str,paras:dict=dict()) -> action.Action:
    act = action.Action(name,paras)
    if act._head == None:
        return None
    return act
