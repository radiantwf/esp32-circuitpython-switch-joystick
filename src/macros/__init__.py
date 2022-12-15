from macros import macro,action
import hid.joystick
import time
import asyncio
import json
import customize.config as config
import customize.task_manager as task_manager

joystick = hid.joystick.JoyStickFactory.get_instance()

TASK_TAG: str = "macros"
_macro_running: bool = False
_realtime_running: bool = False
_current_info = ""
_result_info = ""
_start_time = None
_action_queue = []

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
    global _macro_running
    if _start_time == None or _start_time == 0:
        return "没有正在执行的脚本"
    if not _macro_running :
        return "已收到中止指令，正在处理中"
    span = int(time.time() - _start_time)
    return _current_info + "持续运行时间：{:.0f}小时{:.0f}分{:.0f}秒".format(span/3600, (span % 3600)/60, span % 60)


def result_info():
    global _result_info
    return _result_info

def add_joystick_task(cmd: str):
    try:
        return _create_task_json(json.loads(cmd))
    except:
        global _result_info
        _result_info = "启动命令{}有错误，请检查。".format(cmd)
        return _result_info

def macro_stop():
    global _macro_running
    _macro_running = False
    global _action_queue
    _action_queue = []


def action_queue_task_start():
    tm = task_manager.TaskManager()
    tm.create_task(_run_queue(), TASK_TAG)
    add_joystick_task('{"name":"common.wakeup_joystick","loop":1}')
    

def auto_run():
    c = config.Config()
    try:
        _create_task_json(c.autorun)
    except:
        global _result_info
        _result_info = "Config文件macro.autorun节点存在错误，无法启动脚本"


def _create_task_json(cmd: dict):
    global _action_queue
    realtime_action = cmd.get("realtime")
    if type(realtime_action) is str:
        global _realtime_running
        if realtime_action == "action_start":
            macro_stop()
            _realtime_running = True
            joystick.start_realtime()
            return "开始实时控制模式"
        elif realtime_action == "action_stop":
            _realtime_running = False
            joystick.stop_realtime()
            return "结束实时控制模式"
        else:
            if _realtime_running:
                _action_queue.append((realtime_action,))
                return
    if _realtime_running:
        return
    s = cmd.get("stop")
    c1 = cmd.get("name")
    c2 = cmd.get("loop")
    paras = cmd.get("paras")
    if type(s) is bool and s:
        macro_stop()
        if c1==None:
            return "停止脚本"
    if type(c1) is str:
        name = c1
    else:
        raise
    
    if type(c2) is int:
        loop = c2
    else:
        loop = -1
    try:
        _action_queue.append((name, loop, paras))
        return "{}：已添加任务。".format((name, loop, paras))
    except:
         return "任务队列已满。".format((name, loop, paras))


def published():
    m= macro.Macro()
    if m._publish!= None:
        return json.dumps(m._publish, separators=(',', ':'))
    else:
        return ""

async def _run_queue():
    global _realtime_running
    while True:
        t = None
        global _action_queue
        if len(_action_queue) > 0:
            t = _action_queue[0]
            _action_queue.remove(t)
        if _realtime_running:
            if t == None or len(t)!=1:
                await asyncio.sleep_ms(1)
                continue
            await joystick.send_realtime_action(t[0])
        else:
            if t == None or len(t)<3:
                await asyncio.sleep_ms(10)
                continue
            await _run(t[0],t[1],t[2])
            

async def _run(name: str, loop: int = 1, paras: dict = dict()):
    msg = "开始运行{}脚本，循环次数：{}".format(name, loop)
    print(msg)
    times = 0
    if loop <= 0:
        loop = -1
    global _macro_running
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
        _macro_running = True
        _result_info = ""
        _current_info = "正在运行[{}]脚本，已运行{}次，计划运行{}次\n".format(
            name, times, loop)
        while True:
            while True:
                if not _macro_running:
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
        await joystick.release()
        msg = "脚本{}运行中止，当前运行次数：{}".format(name, times)
        print(msg)
        span = time.time() - start_ts
        _result_info = "脚本[{}]停止，实际运行{}次，计划运行{}次\n持续运行时间：{:.0f}小时{:.0f}分{:.0f}秒".format(
            name, times, loop, span/3600, (span % 3600)/60, span % 60)
    finally:
        _start_time = None
        _macro_running = False
        _current_info = ""


def _get_action(name: str,paras:dict=dict()) -> action.Action:
    act = action.Action(name,paras)
    if act._head == None:
        return None
    return act
