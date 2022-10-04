from io import StringIO
from ui.ui_win import Ui_MainWindow
from PySide6 import QtWidgets
from datatype.device import AudioDevice
from PySide6.QtCore import Slot,Qt,QEvent,QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtMultimedia import QAudioFormat,QAudioSource,QAudioSink,QMediaDevices
from ui.video import VideoThread
import time

class UserWindows(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self,frame_queue,processed_frame_queue,dev:AudioDevice,video_with,video_height):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self._audio_device = dev
        self._video_with = video_with
        self._video_height = video_height
        self._frame_queue = frame_queue
        self._processed_frame_queue = processed_frame_queue
        self._key_press_map = dict()
        self._last_sent_action = ""
        self._last_sent_ts = time.monotonic()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            self._key_press_map[event.key()] = time.monotonic()
        elif event.type() == QEvent.Type.KeyRelease:
            self._key_press_map.pop(event.key(),None)
        elif event.type() == QEvent.Type.FocusOut:
            self._key_press_map.clear()

        count = 0
        if self._key_press_map.get(Qt.Key_A):
            count += 1
        if self._key_press_map.get(Qt.Key_S):
            count += 1
        if self._key_press_map.get(Qt.Key_D):
            count += 1
        if self._key_press_map.get(Qt.Key_W):
            count += 1
        if count > 2:
            self._key_press_map.pop(Qt.Key_A,None)
            self._key_press_map.pop(Qt.Key_S,None)
            self._key_press_map.pop(Qt.Key_D,None)
            self._key_press_map.pop(Qt.Key_W,None)
        if self._key_press_map.get(Qt.Key_A) and self._key_press_map.get(Qt.Key_D):
            self._key_press_map.pop(Qt.Key_A,None)
            self._key_press_map.pop(Qt.Key_D,None)
        if self._key_press_map.get(Qt.Key_S) and self._key_press_map.get(Qt.Key_W):
            self._key_press_map.pop(Qt.Key_S,None)
            self._key_press_map.pop(Qt.Key_W,None)
        
        count = 0
        if self._key_press_map.get(Qt.Key_Semicolon):
            count += 1
        if self._key_press_map.get(Qt.Key_Comma):
            count += 1
        if self._key_press_map.get(Qt.Key_Period):
            count += 1
        if self._key_press_map.get(Qt.Key_Slash):
            count += 1
        if count > 2:
            self._key_press_map.pop(Qt.Key_Semicolon,None)
            self._key_press_map.pop(Qt.Key_Comma,None)
            self._key_press_map.pop(Qt.Key_Period,None)
            self._key_press_map.pop(Qt.Key_Slash,None)
        if self._key_press_map.get(Qt.Key_Semicolon) and self._key_press_map.get(Qt.Key_Period):
            self._key_press_map.pop(Qt.Key_Semicolon,None)
            self._key_press_map.pop(Qt.Key_Period,None)
        if self._key_press_map.get(Qt.Key_Period) and self._key_press_map.get(Qt.Key_Slash):
            self._key_press_map.pop(Qt.Key_Period,None)
            self._key_press_map.pop(Qt.Key_Slash,None)

        count = 0
        if self._key_press_map.get(Qt.Key_F):
            count += 1
        if self._key_press_map.get(Qt.Key_C):
            count += 1
        if self._key_press_map.get(Qt.Key_V):
            count += 1
        if self._key_press_map.get(Qt.Key_B):
            count += 1
        if count > 1:
            self._key_press_map.pop(Qt.Key_F,None)
            self._key_press_map.pop(Qt.Key_C,None)
            self._key_press_map.pop(Qt.Key_V,None)
            self._key_press_map.pop(Qt.Key_B,None)
        if self._key_press_map.get(Qt.Key_F) and self._key_press_map.get(Qt.Key_V):
            self._key_press_map.pop(Qt.Key_F,None)
            self._key_press_map.pop(Qt.Key_V,None)
        if self._key_press_map.get(Qt.Key_C) and self._key_press_map.get(Qt.Key_B):
            self._key_press_map.pop(Qt.Key_C,None)
            self._key_press_map.pop(Qt.Key_B,None)

        
        return QtWidgets.QMainWindow.eventFilter(self, obj, event)

        
    def key_send(self):
        self._set_joystick_label(Qt.Key_A,self.label_a)
        self._set_joystick_label(Qt.Key_W,self.label_w)
        self._set_joystick_label(Qt.Key_S,self.label_s)
        self._set_joystick_label(Qt.Key_D,self.label_d)
        self._set_joystick_label(Qt.Key_X,self.label_x)

        self._set_joystick_label(Qt.Key_Semicolon,self.label_rt)
        self._set_joystick_label(Qt.Key_Comma,self.label_rl)
        self._set_joystick_label(Qt.Key_Period,self.label_rb)
        self._set_joystick_label(Qt.Key_Slash,self.label_rr)
        self._set_joystick_label(Qt.Key_Apostrophe,self.label_rc)

        self._set_joystick_label(Qt.Key_F,self.label_f)
        self._set_joystick_label(Qt.Key_C,self.label_c)
        self._set_joystick_label(Qt.Key_B,self.label_b)
        self._set_joystick_label(Qt.Key_V,self.label_v)

        self._set_joystick_label(Qt.Key_T,self.label_t)
        self._set_joystick_label(Qt.Key_Y,self.label_y)
        self._set_joystick_label(Qt.Key_G,self.label_g)
        self._set_joystick_label(Qt.Key_H,self.label_h)

        self._set_joystick_label(Qt.Key_Q,self.label_q)
        self._set_joystick_label(Qt.Key_E,self.label_e)
        self._set_joystick_label(Qt.Key_O,self.label_o)
        self._set_joystick_label(Qt.Key_U,self.label_u)

        self._set_joystick_label(Qt.Key_I,self.label_i)
        self._set_joystick_label(Qt.Key_J,self.label_j)
        self._set_joystick_label(Qt.Key_L,self.label_l)
        self._set_joystick_label(Qt.Key_K,self.label_k)

        action = self._get_action_line()
        
        if action != self._last_sent_action or time.monotonic() - self._last_sent_ts > 5:
            self._last_sent_action = action
            self._last_sent_ts = time.monotonic()
            self.label_action.setText("实时命令：{}".format(action))
        self.repaint()
        
    
    def _set_joystick_label(self,key,label):
        if self._key_press_map.get(key) != None:
            label.setStyleSheet(u"background-color:rgb(0, 0, 255)")
        else:
            label.setStyleSheet(u"background-color:rgb(209, 209, 209)")
    
    def _get_action_line(self)->str:
        sio = StringIO()
        if self._key_press_map.get(Qt.Key_L):
            sio.write("A|")
        if self._key_press_map.get(Qt.Key_K):
            sio.write("B|")
        if self._key_press_map.get(Qt.Key_I):
            sio.write("X|")
        if self._key_press_map.get(Qt.Key_J):
            sio.write("Y|")
            
        if self._key_press_map.get(Qt.Key_E):
            sio.write("L|")
        if self._key_press_map.get(Qt.Key_Q):
            sio.write("ZL|")
        if self._key_press_map.get(Qt.Key_U):
            sio.write("R|")
        if self._key_press_map.get(Qt.Key_O):
            sio.write("ZR|")

        if self._key_press_map.get(Qt.Key_T):
            sio.write("MINUS|")
        if self._key_press_map.get(Qt.Key_Y):
            sio.write("PLUS|")
        if self._key_press_map.get(Qt.Key_G):
            sio.write("CAPTURE|")
        if self._key_press_map.get(Qt.Key_H):
            sio.write("HOME|")

        if self._key_press_map.get(Qt.Key_F):
            sio.write("TOP|")
        if self._key_press_map.get(Qt.Key_C):
            sio.write("LEFT|")
        if self._key_press_map.get(Qt.Key_V):
            sio.write("BOTTOM|")
        if self._key_press_map.get(Qt.Key_B):
            sio.write("RIGHT|")
        
        if self._key_press_map.get(Qt.Key_X):
            sio.write("LPRESS|")
        if self._key_press_map.get(Qt.Key_Apostrophe):
            sio.write("RPRESS|")
        x = 0
        y = 0
        if self._key_press_map.get(Qt.Key_W):
            y = 127
        elif self._key_press_map.get(Qt.Key_S):
            y = -127
        if self._key_press_map.get(Qt.Key_D):
            x = 127
        elif self._key_press_map.get(Qt.Key_A):
            x = -127
        if x != 0 or y !=0:
            sio.write("LSTICK@{},{}|".format(x,y))
        x = 0
        y = 0
        if self._key_press_map.get(Qt.Key_Semicolon):
            y = 127
        elif self._key_press_map.get(Qt.Key_Period):
            y = -127
        if self._key_press_map.get(Qt.Key_Period):
            x = 127
        elif self._key_press_map.get(Qt.Key_Comma):
            x = -127
        if x != 0 or y !=0:
            sio.write("RSTICK@{},{}|".format(x,y))
        sio.flush()
        action = sio.getvalue()
        sio.close()
        return action
    
    def setupUi(self):
        Ui_MainWindow.setupUi(self,self)
        self.th_video = VideoThread(self)
        self.th_video.set_input(self._video_with,self._video_height,3,QImage.Format_BGR888,self._frame_queue)
        self.th_video.video_frame.connect(self.setImage2)
        self.th_video.start()
        self.th_processed = VideoThread(self)
        self.th_processed.set_input(self._video_with,self._video_height,3,QImage.Format_BGR888,self._processed_frame_queue)
        self.th_processed.video_frame.connect(self.setImage1)
        self.th_processed.start()
        self.play_audio()
        self.timer = QTimer()
        self.timer.timeout.connect(self.key_send)
        self.timer.start(5)
        self.destroyed.connect(self.on_destroy)

    def play_audio(self):
        if not self._audio_device:
            return
        format_audio = QAudioFormat()
        format_audio.setSampleRate(44100)
        format_audio.setChannelCount(2)
        format_audio.setSampleFormat(QAudioFormat.Int16)

        for dev in QMediaDevices.audioInputs():
            if dev.description() == self._audio_device.name:
                self._audio_input = QAudioSource(dev, format_audio, self)
                self._io_device = self._audio_input.start()
                self._io_device.readyRead.connect(self._readyRead)
                break

        self._output_device = QMediaDevices.defaultAudioOutput()
        self._m_audioSink = QAudioSink(self._output_device, format_audio)
        self._m_output= self._m_audioSink.start()

    @Slot(QImage)
    def setImage1(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    @Slot(QImage)
    def setImage2(self, image):
        pixmap = QPixmap.fromImage(image).scaled(self.label_2.size(), aspectMode=Qt.KeepAspectRatio)
        self.label_2.setPixmap(pixmap)

    @Slot()
    def on_destroy(self):
        self._frame_queue.close()
        self.timer.stop()
        self.th_video.terminate()
        self.th_processed.terminate()
        # self.th_audio.terminate()
        if self._audio_input != None:
            self._audio_input.stop()
        self._m_audioSink.stop()
        # self._audio_input.stop()
        # self._io_device.stop()
    

    @Slot()
    def _readyRead(self):
        data = self._io_device.readAll()
        self._m_output.write(data)
        