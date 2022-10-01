import io
import macros
import time
import asyncio
from errno import EAGAIN
import wifi
import socketpool
import customize.wifi_connect as wifi_connect
import customize.task_manager as task_manager

MAXBUF = 1024

class TcpServer(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(TcpServer, cls).__new__(cls)
        return cls._instance

    _first = True
    def __init__(self):
        if self._first:
            self._first = False
            self._on_message = None
            self._socket: socketpool.Socket = None
            self._clients = []

    async def start_serve(self,port):
        tm = task_manager.TaskManager()
        HOST = ""
        pool = socketpool.SocketPool(wifi.radio)
        HOST = str(wifi_connect.ip_address())
        print("Create TCP Server socket")
        self._socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        self._socket.settimeout(0)
        self._socket.bind((HOST, port))
        self._socket.listen(1000)
        while True:
            await asyncio.sleep_ms(10)
            try:
                client = None
                try:
                    s = self._socket.accept()
                    client = s[0]
                except OSError as e:
                    if e.errno != EAGAIN:
                        raise e
                self._clients.append(client)
                client.settimeout(0)
                tm.create_task(self.tcp_handler(client))
            except:
                if client != None:
                    self._clients.remove(client)

    async def tcp_handler(self, client_socket):
        buf = bytearray(MAXBUF)
        last_active_ts = time.monotonic()
        try:
            size = 0
            while True:
                await asyncio.sleep_ms(10)
                if time.monotonic() - last_active_ts > 10:
                    client_socket.send("ping".encode('utf-8'))
                    last_active_ts = time.monotonic()
                bytes_io = io.BytesIO()
                while True:
                    try:
                        size = client_socket.recv_into(buf,MAXBUF)
                        bytes_io.write(buf[:size])
                    except OSError as e:
                        if e.errno == EAGAIN:
                            break
                        raise e
                data = bytes_io.getvalue()
                bytes_io.close()
                if len(data) > 0 :
                    last_active_ts = time.monotonic()
                    data = data.decode('utf-8')
                    ret = macros.add_joystick_task(data)
                    client_socket.send(ret.encode('utf-8'))
                    # client_socket.send(data.encode('utf-8'))

        except:
            self._clients.remove(client_socket)