from capture import video
import datatype.device as device

def capture_video(pipe,dev:device.VideoDevice,display_width,display_height,display_fps):
	video.Video().run(pipe,dev,display_width,display_height,display_fps)
