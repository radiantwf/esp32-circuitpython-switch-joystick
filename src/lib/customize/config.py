import json


class Config(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    _first = True

    def __init__(self):
        if Config._first:
            Config._first = False
            self._config = dict()
            self._autorun = None
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
            if type(v) is dict:
                if p == "macros.autorun":
                    self._autorun = v
                ret = self._analyze_config(v, p, ret)
            else:
                ret[p] = v
        return ret

    def get(self, condition: str, type=""):
        if condition == None or condition == "":
            return None
        else:
            if type == None or type == "":
                key = condition
            else:
                key = "{}.{}".format(type, condition)
            v = self._config.get(key)
            return v

    def reset(self):
        self._config.clear()
        self._autorun = None
        self._load_file()

    @property
    def autorun(self):
        return self._autorun