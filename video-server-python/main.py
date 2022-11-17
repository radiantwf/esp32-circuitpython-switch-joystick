import capture
import controller
import datatype.device as device
import recognize
import ui
import sys
import multiprocessing
import time

_Camera_Name = "USB Video"
_Camera_Width = 1280
_Camera_Height = 720
_Camera_FPS = 60

_Audio_Device_Name = "数字音频接口 ({})".format("USB Digital Audio")

_Display_Width = 960
_Display_Height = 540
_Display_FPS = 60
_Recognize_FPS = 30

# _Camera_Name = "FaceTime高清摄像头（内建）"
# _Camera_FPS = 30
# _Audio_Device_Name = "内建麦克风"

# _Camera_Name = "Game Capture HD60 S+"
# _Audio_Device_Name = "Digital Audio Interface ({})".format( "Game Capture HD60 S+")

def main():
    dev_video = device.VideoDevice(name=_Camera_Name,width=_Camera_Width,height=_Camera_Height,fps=_Camera_FPS,index=0,pix_fmt=None)
    # dev_video = device.VideoDevice(name=_Camera_Name,width=_Camera_Width,height=_Camera_Height,fps=_Camera_FPS,index=0,pix_fmt=None,vcodec="mjpeg")
    # dev_video = device.VideoDevice(name=_Camera_Name,width=_Camera_Width,height=_Camera_Height,fps=_Camera_FPS,index=1,pix_fmt="bgr0")
    dev_audio = device.AudioDevice(name=_Audio_Device_Name,sample_rate=44100,channels=2)
    dev_joystick = device.JoystickDevice(host="192.168.50.120",port=5000)
    main_video_frame,capture_video_frame = multiprocessing.Pipe(False)
    ui_display_video_frame = multiprocessing.Queue()
    opencv_processed_video_frame = multiprocessing.Queue()
    recognize_video_frame = multiprocessing.Queue(1)
    frame_queues = (recognize_video_frame,ui_display_video_frame,opencv_processed_video_frame,)
    controller_action_queue = multiprocessing.Queue()
    opencv_processed_control_queue = multiprocessing.Queue()
    control_queues=(opencv_processed_control_queue,controller_action_queue,)
    controller_process = multiprocessing.Process(target=controller.run, args=(dev_joystick,control_queues,))
    controller_process.start()
    ui_process = multiprocessing.Process(target=ui.run, args=(frame_queues,control_queues,dev_audio,_Display_Width,_Display_Height))
    ui_process.start()
    recognize_process = multiprocessing.Process(target=recognize.run, args=(frame_queues,control_queues,_Display_Width,_Display_Height,_Recognize_FPS,))
    recognize_process.start()
    video_process = multiprocessing.Process(target=capture.capture_video, args=(capture_video_frame,dev_video,_Display_Width,_Display_Height,_Display_FPS,))
    video_process.start()
    try:
        while True:
            if not ui_process.is_alive():
                break
            video_frame = main_video_frame.recv()
            try:
                ui_display_video_frame.put(video_frame,False,0)
            except:
                pass
            try:
                recognize_video_frame.put(video_frame,False,0)
            except:
                pass
            time.sleep(0.001)
        sys.exit(0)
    except:
        pass
    finally:
        controller_process.kill()
        video_process.kill()
        recognize_process.kill()
        ui_process.kill()

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    main()

