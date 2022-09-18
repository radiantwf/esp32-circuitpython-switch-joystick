import json


class Config(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._config = dict()
        self._load_file()

    def _load_file(self):
        try:
            f = open("/resources/config.json", "rt")
            c = json.load(f)
            f.close()
        except:
            if f != None:
                f.close()
            return
        self._config = self._analyze_config(c)

    def _analyze_config(self, d: dict, path: str = "", ret: dict = dict()) -> dict:
        for key in d.keys():
            if path == "":
                p = key
            else:
                p = path + "." + key
            v = d.get(key)
            if type(v) is bool:
                ret[p] = v
            elif type(v) is dict:
                ret = self._analyze_config(v, p, ret)
        return ret

    def set_running_setting(self, key: str, value: bool):
        self._config["running."+key] = value

    def check(self, running_condition: str) -> bool:
        if running_condition == None or running_condition == "":
            return True
        else:
            v = self._config.get("running."+running_condition)
            if type(v) is bool:
                return v
            v = self._config.get(running_condition)
            if type(v) is bool:
                return v
        return False

    def reset(self):
        self._config.clear()
        self._load_file()
