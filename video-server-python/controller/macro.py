import json
import time

class Action(object):
    def __init__(self) -> None:
        self._dict = dict()
        self.ts = time.monotonic()

    @property
    def message(self):
        return json.dumps(self._dict)

    @property
    def type(self):
        return "action"

    def get(self,key):
        return self._dict.get(key)

class Macro(Action):
    def __init__(self,stop:bool,name:str,loop:int = 1,paras:dict = dict()) -> None:
        super().__init__()
        if stop:
            self._dict["stop"] = True
            if name == None:
                return
        else:
            self._dict["stop"] = False
        self._dict["name"] = name
        self._dict["loop"] = loop
        self._dict["paras"] = paras

    @property
    def type(self):
        return "macro"


macro_action_clear = Macro(True,name=None)
macro_close_game = Macro(True,name="common.close_game",loop=1)
macro_press_button_a_loop = Macro(False,name="common.press_button_a",loop=100)

class Realtime(Action):
    def __init__(self,action_line:str) -> None:
        super().__init__()
        self._dict["realtime"] = action_line

    @property
    def type(self):
        return "realtime"

realtime_action_start = Realtime("action_start")
realtime_action_stop = Realtime("action_stop")

_public_macro_dict = dict()
_public_macro_dict["雷吉艾勒奇"] = Macro(True,name="雷吉艾勒奇（定点）",loop=99999999,paras={"secondary":"False"})
_public_macro_dict["雷吉洛克/雷吉斯奇鲁"] = Macro(True,name="雷吉洛克/雷吉斯奇鲁（定点）",loop=99999999,paras={"secondary":"False"})
_public_macro_dict["饲育屋取蛋"] = Macro(True,name="饲育屋取蛋",loop=1000)

def public_macros():
    return _public_macro_dict.keys()

def get_public_macro(key) -> Macro:
    return _public_macro_dict.get(key)