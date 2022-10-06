
import socket
import time
from PySide6.QtCore import QThread,Signal


class LogThread(QThread):
    log = Signal(str)
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self._udp_socket = None

    def set_port(self,port = 41001):
        self._port = port
        
    def run(self):
        while True:
            try:
                if self._udp_socket:
                    s = self._udp_socket
                    self._udp_socket = None
                    s.close()
                self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
                local_addr = ("127.0.0.1", self._port) 
                self._udp_socket.bind(local_addr)
                self._udp_socket.setblocking(False)
                while True:
                    recv_data = None
                    try:
                        recv_data = self._udp_socket.recvfrom(1024)
                    except Exception as e:
                        pass
                    if recv_data != None:
                        recv_msg = recv_data[0].decode("utf-8").strip()
                        self.log.emit(recv_msg)
                    time.sleep(0.001)
            except:
                continue

    def quit(self):
        if self._udp_socket:
            self._udp_socket.close()