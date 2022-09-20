import wifi
import socketpool
import asyncio
from . import wifi_connect
from . import config
import time


class UdpServer(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(UdpServer, cls).__new__(cls)
        return cls._instance

    _first = True

    def __init__(self):
        if self._first:
            self._first = False
            self._on_message = None
            self._socket: socketpool.Socket = None
            self._broadcast_dict = dict()
            self._server_running = False

    @property
    async def on_message(self):
        return self._on_message

    @on_message.setter
    def on_message(self, method):
        self._on_message = method

    async def start_serve(self):
        HOST = ""
        TIMEOUT = 0
        MAXBUF = 1024
        pool = socketpool.SocketPool(wifi.radio)
        HOST = str(wifi_connect.ip_address())
        print("Self IP", HOST)

        print("Create UDP Server socket")
        self._socket = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)
        self._socket.settimeout(TIMEOUT)
        port = 5001
        respond_port = 35001

        _config = config.Config()
        try:
            p1 = int(_config.get("udp.listening_port"))
        except:
            p1 = 0
        try:
            p2 = int(_config.get("udp.respond_port"))
        except:
            p2 = 0
        if p1 > 0 and p1 < 65535:
            port = p1
        if p2 > 0 and p2 < 65535:
            respond_port = p2
        self._socket.bind((HOST, port))
        self._server_running = True

        buf = bytearray(MAXBUF)
        while True:
            try:
                size, addr = self._socket.recvfrom_into(buf)
                if size > 0 and self._on_message != None:
                    self._broadcast_dict[addr[0]] = time.time()
                    des = (addr[0], respond_port)
                    await self._on_message(buf[:size].decode('utf-8'), des)
            except OSError:
                size = 0
            if size < MAXBUF:
                await asyncio.sleep_ms(10)
        # size = _socket.sendto(buf[:size], addr)
        # print("Sent", buf[:size], size, "bytes to", addr)

    def send_message(self, msg: str, addr):
        if not self._server_running:
            return
        if msg == None or len(msg) == 0:
            return
        self._socket.sendto(msg.encode('utf-8'), addr)

    def broadcast_message(self, msg: str):
        if not self._server_running:
            return
        if msg == None or len(msg) == 0:
            return
        removes = []
        respond_port = 35001
        _config = config.Config()
        try:
            p2 = int(_config.get("udp.respond_port"))
        except:
            p2 = 0
        if p2 > 0 and p2 < 65535:
            respond_port = p2
        now = time.time()
        for ip in self._broadcast_dict.keys():
            if now - self._broadcast_dict[ip] <= 3600:
                self._socket.sendto(msg.encode('utf-8'), (ip, respond_port))
            else:
                removes.append(ip)
        for ip in removes:
            self._broadcast_dict.pop(ip)
