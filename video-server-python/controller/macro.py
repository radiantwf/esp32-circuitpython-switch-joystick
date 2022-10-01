import json
class Macro(object):
    def __init__(self,stop:bool,name:str,loop:int = 1,paras:dict = dict()) -> None:
        self._dict = dict()
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
    def message(self):
        return json.dumps(self._dict).encode("utf-8")

macro_action_clear = Macro(True,None)
macro_close_game = Macro(True,name="common.close_game",loop=1)
macro_press_button_a_loop = Macro(False,name="common.press_button_a",loop=100)