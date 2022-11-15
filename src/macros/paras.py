class Paras(object):
    def __init__(self, default_para: dict,para:dict):
        self._paras = None
        if default_para != None:
            self._paras = default_para.copy()
        else:
            self._paras = dict()

        if para != None:
            for key in para.keys():
                v = para[key]
                if v != None and v != "":
                    self._paras[key] = v

    def get_bool(self,key)->bool:
        locals().update(self._paras)
        try:
            v = eval(key)
        except:
            return False
        if v == None:
            return False
        elif (type(v) is bool):
            return v
        elif (type(v) is str) and v.lower() == "true":
            return True
        return False
    
    def get_int(self,key)->int:
        locals().update(self._paras)
        try:
            v = eval(key)
        except:
            return 0

        if v == None:
            return 0
        elif (type(v) is int):
            return v
        elif (type(v) is float):
            return int(v)
        elif (type(v) is str):
            return int(float(v))
        return 0
