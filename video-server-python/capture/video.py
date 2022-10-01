import os
import sys
from typing import Any
import datatype.device as device
import ffmpeg

class Video():
    def __init__(self):
        pass

    def _start_ffmpeg(self,dev:device.VideoDevice,display_width,display_height,display_fps):
        if dev == None:
            return
        
        input_paras = dict[str,Any]()
        input_paras["framerate"] = dev.fps
        input_paras["s"] = "{}*{}".format(dev.width,dev.height)
        input_paras["format"] = dev.format
        
        if dev.pix_fmt != None:
            input_paras["pix_fmt"] = dev.pix_fmt
        if dev.vcodec != None:
            input_paras["vcodec"] = dev.vcodec
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        process = (
            ffmpeg
            .input("{}".format(dev.ffmepg_name),**input_paras)
            .output(
                "pipe:",
                f='rawvideo',
                pix_fmt='bgr24',
                r=display_fps,
                s="{}*{}".format(display_width,display_height),
            )
            .run_async(pipe_stdout=True,)
            # .run_async(quiet=True,pipe_stdout=True)
        )
        return process
        
    def run(self,pipe,dev:device.VideoDevice,display_width,display_height,display_fps):
        process = self._start_ffmpeg(dev,display_width,display_height,display_fps)
        while True:
            frame_bytes = process.stdout.read(display_width * display_height * 3)
            if not frame_bytes:
                break
            if pipe.writable:
                pipe.send(frame_bytes)
            else:
                break
        process.terminate()