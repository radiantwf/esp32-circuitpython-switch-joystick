
import sys
from PySide6 import QtWidgets
from datatype.device import AudioDevice
from ui.user_window import UserWindows
def run(frame_queue,processed_frame_queue,dev:AudioDevice,video_with,video_height):
    _show(frame_queue,processed_frame_queue,dev,video_with,video_height)

def _show(frame_queue,processed_frame_queue,dev:AudioDevice,video_with,video_height):
    app = QtWidgets.QApplication()
    MainWindow = QtWidgets.QMainWindow()
    ui = UserWindows(frame_queue,processed_frame_queue,dev,video_with,video_height)
    ui.setupUi(MainWindow)
    MainWindow.show()
    ret = app.exec_()
    sys.exit(ret)