from ui.ui_win import Ui_MainWindow

from datatype.device import AudioDevice
from PySide6.QtCore import Slot,Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtMultimedia import QAudioFormat,QAudioSource,QAudioSink,QMediaDevices

from ui.video import VideoThread


class UserWindows(Ui_MainWindow):
    def __init__(self,frame_queue,processed_frame_queue,dev:AudioDevice,video_with,video_height):
        super().__init__()
        self._audio_device = dev
        self._video_with = video_with
        self._video_height = video_height
        self._frame_queue = frame_queue
        self._processed_frame_queue = processed_frame_queue

    def setupUi(self,MainWindow):
        super().setupUi(MainWindow)
        self.th_video = VideoThread(MainWindow)
        self.th_video.set_input(self._video_with,self._video_height,3,QImage.Format_BGR888,self._frame_queue)
        self.th_video.video_frame.connect(self.setImage2)
        self.th_video.start()
        self.th_processed = VideoThread(MainWindow)
        self.th_processed.set_input(self._video_with,self._video_height,3,QImage.Format_BGR888,self._processed_frame_queue)
        self.th_processed.video_frame.connect(self.setImage1)
        self.th_processed.start()
        self.play_audio(MainWindow)
        MainWindow.destroyed.connect(self.on_destroy)

    def play_audio(self,MainWindow):
        format_audio = QAudioFormat()
        format_audio.setSampleRate(44100)
        format_audio.setChannelCount(2)
        format_audio.setSampleFormat(QAudioFormat.Int16)

        for dev in QMediaDevices.audioInputs():
            if dev.description() == self._audio_device.name:
                self._audio_input = QAudioSource(dev, format_audio, MainWindow)
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
        