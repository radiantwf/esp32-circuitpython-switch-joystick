
from PySide6.QtCore import QThread,Signal
from PySide6.QtGui import QImage


class VideoThread(QThread):
    video_frame = Signal(QImage)
    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def set_input(self,width,height,channels,format,queue):
        self._width = width
        self._height = height
        self._channels = channels
        self._format = format
        self._queue = queue
        
    def run(self):
        while True:
            if self._queue != None :
                frame = self._queue.get()
                img = QImage(frame, self._width, self._height, self._channels*self._width,self._format)
                self.video_frame.emit(img)