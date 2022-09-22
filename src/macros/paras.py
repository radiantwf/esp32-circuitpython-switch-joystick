


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
        v = self._paras.get(key)
        if v == None and not (type(v) is str):
            return False
        elif v.lower() == "true":
            return True
        return False
    
    def get_int(self,key)->int:
        v = self._paras.get(key)
        if v == None and not (type(v) is str):
            return 1
        try:
            return int(float(v))
        except:
            return 1