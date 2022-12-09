import io
import macros
import time
import asyncio
from errno import EAGAIN,ENOTCONN
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
        if TcpServer._first:
            TcpServer._first = False
            self._on_message = None
            self._socket: socketpool.Socket = None
            self._clients = []

    async def start_serve(self,port):
        tm = task_manager.TaskManager()
        HOST = None
        HOST = wifi_connect.ip_address()
        if HOST == None:
            await asyncio.sleep(5)
            if self._socket != None:
                self._socket.close()
                self._socket: socketpool.Socket = None
                self._clients = []
            try:
                wifi_connect.reconnect()
            except:
                pass
            tm.create_task(self.start_serve(port))
            return
        print("Starting TCP Server socket")
        pool = socketpool.SocketPool(wifi.radio)
        self._socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        self._socket.setblocking(False)
        self._socket.bind((str(HOST), port))
        self._socket.listen(1000)

        while True:
            await asyncio.sleep_ms(10)
            if wifi_connect.ip_address() == None:
                 tm.create_task(self.start_serve(port))
                 self._socket.close()
                 return
            try:
                client = None
                try:
                    s = self._socket.accept()
                    client = s[0]
                except OSError as e:
                    if e.errno != EAGAIN:
                        raise e
                if client != None:
                    self._clients.append(client)
                    client.setblocking(False)
                    tm.create_task(self.tcp_handler(client))
            except OSError as e:
                if client != None:
                    self._clients.remove(client)

    async def tcp_handler(self, client_socket):
        buf = bytearray(MAXBUF)
        last_active_ts = time.monotonic()
        try:
            size = 0
            while True:
                await asyncio.sleep_ms(1)
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
                        elif e.errno == ENOTCONN:
                            data = bytes_io.getvalue()
                            bytes_io.close()
                            if len(data) > 0 :
                                last_active_ts = time.monotonic()
                                data = data.decode('utf-8')
                                ret = macros.add_joystick_task(data)
                            self._clients.remove(client_socket)
                            return
                        raise e
                data = bytes_io.getvalue()
                bytes_io.close()
                if len(data) > 0 :
                    last_active_ts = time.monotonic()
                    data = data.decode('utf-8')
                    ret = macros.add_joystick_task(data)
                    if ret and ret != "":
                        client_socket.send(ret.encode('utf-8'))
                    # client_socket.send(data.encode('utf-8'))
        except:
            self._clients.remove(client_socket)