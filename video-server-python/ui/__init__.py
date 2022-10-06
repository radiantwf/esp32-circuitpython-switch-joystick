
import sys
from PySide6 import QtWidgets
from datatype.device import AudioDevice
from ui.user_window import UserWindows
def run(frame_queues,control_queues,dev:AudioDevice,video_with,video_height):
    _show(frame_queues,control_queues,dev,video_with,video_height)

def _show(frame_queues,control_queues,dev:AudioDevice,video_with,video_height):
    app = QtWidgets.QApplication()
    _main_window = UserWindows(frame_queues,control_queues,dev,video_with,video_height)
    app.installEventFilter(_main_window)
    _main_window.setupUi()
    _main_window.show()
    ret = app.exec_()
    sys.exit(ret)