import platform
class VideoDevice(object):
    def __init__(self,name:str,width:int,height:int,fps:int,index:int=0,pix_fmt:str = None,vcodec:str = None):
        self._name = name
        self._width = width
        self._height = height
        self._fps = fps
        self._pix_fmt = pix_fmt
        self._vcodec = vcodec
        self._index = index
        self._sys_str = platform.system()

    @property
    def name(self):
        return self._name
    @property
    def ffmepg_name(self):
        if self._sys_str == "Windows":
            return "video={}".format(self._name)
        else:
            return self._name
    @property
    def width(self):
        return self._width
    @property
    def height(self):
        return self._height
    @property
    def format(self):
        _format = ''
        if self._sys_str == "Windows":
            _format = 'dshow'
        elif self._sys_str == "Darwin":
            _format = 'avfoundation'
        else:
            _format = 'video4linux2'
        return _format
    @property
    def fps(self):
        return self._fps
    @property
    def index(self):
        return self._index
    @property
    def pix_fmt(self):
        return self._pix_fmt
    @property
    def vcodec(self):
        return self._vcodec

class AudioDevice(object):
    def __init__(self,name:str,sample_rate:int,channels:int):
        self._name = name
        self._sample_rate = sample_rate
        self._channels = channels
        self._sys_str = platform.system()
    
    @property
    def name(self):
        return self._name

    @property
    def ffmepg_name(self):
        if self._sys_str == "Windows":
            return "audio=数字音频接口 ({})".format(self._name)
        else:
            return ":{}".format(self._name)

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def channels(self):
        return self._channels

    @property
    def format(self):
        _format = ''
        sys_str = platform.system()
        if sys_str == "Windows":
            _format = 'dshow'
        elif sys_str == "Darwin":
            _format = 'avfoundation'
        else:
            _format = 'alsa'
        return _format

class JoystickDevice(object):
    def __init__(self,host:str,port:int):
        self._host = host
        self._port = port
    
    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port
