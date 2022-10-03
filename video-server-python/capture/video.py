import datatype.device as device
import cv2
import time
from PySide6.QtMultimedia import (QMediaDevices)
class Video():
    def __init__(self):
        pass

    # def _start_ffmpeg(self,dev:device.VideoDevice,display_width,display_height,display_fps):
    #     if dev == None:
    #         return
        
    #     input_paras = dict[str,Any]()
    #     input_paras["framerate"] = dev.fps
    #     input_paras["s"] = "{}*{}".format(dev.width,dev.height)
    #     input_paras["format"] = dev.format
        
    #     if dev.pix_fmt != None:
    #         input_paras["pix_fmt"] = dev.pix_fmt
    #     if dev.vcodec != None:
    #         input_paras["vcodec"] = dev.vcodec
    #     sys.stdout = open(os.devnull, 'w')
    #     sys.stderr = open(os.devnull, 'w')
    #     process = (
    #         ffmpeg
    #         .input("{}".format(dev.ffmepg_name),**input_paras)
    #         .output(
    #             "pipe:",
    #             f='rawvideo',
    #             pix_fmt='bgr24',
    #             r=display_fps,
    #             s="{}*{}".format(display_width,display_height),
    #         )
    #         .run_async(pipe_stdout=True,)
    #         # .run_async(quiet=True,pipe_stdout=True)
    #     )
    #     return process
        
    def run(self,pipe,dev:device.VideoDevice,display_width,display_height,display_fps):
        if dev == None:
            return
        self.capture(pipe,dev,display_width,display_height,display_fps)
        # process = self._start_ffmpeg(dev,display_width,display_height,display_fps)
        # while True:
        #     frame_bytes = process.stdout.read(display_width * display_height * 3)
        #     if not frame_bytes:
        #         break
        #     if pipe.writable:
        #         pipe.send(frame_bytes)
        #     else:
        #         break
        # process.terminate()

    def capture(self,pipe,dev:device.VideoDevice,display_width,display_height,display_fps:int):
        available_cameras = QMediaDevices.videoInputs()
        cap = cv2.VideoCapture(dev.index,cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,dev.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,dev.height)
        cap.set(cv2.CAP_PROP_POS_FRAMES,dev.fps)
        cap.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc(*'MJPG'))
        if display_fps <= 0:
            display_fps = dev.fps
        last_cap_monotonic = time.monotonic()
        min_interval = 1 / display_fps
        while cap.isOpened():
            ret, frame = cap.read()
            now = time.monotonic()
            if now - last_cap_monotonic >= min_interval:
                last_cap_monotonic = now
                frame = cv2.resize(frame, (display_width, display_height))
                if pipe.writable:
                    pipe.send(frame.tobytes())
        cap.release()
        cv2.destroyAllWindows()