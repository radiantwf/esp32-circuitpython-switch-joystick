
import sys
from PySide6 import QtWidgets
from ui.user_window import UserWindows
def main():
    _show()

def _show():
    app = QtWidgets.QApplication()
    _main_window = UserWindows(None,None,None,None,None)
    app.installEventFilter(_main_window)
    _main_window.setupUi()
    _main_window.show()
    ret = app.exec_()
    sys.exit(ret)

    
if __name__ == "__main__":
    main()