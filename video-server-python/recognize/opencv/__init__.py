from recognize import frame
from recognize.opencv.battle_shiny import BattleShiny
from recognize.opencv.none_opencv import NoneOpenCV

_opencv_list = []
_opencv_list.append("定点闪（A连点）")

def opencv_list():
	return _opencv_list


def create_instance(tag,frame:frame.Frame,opencv_processed_video_frame,controller_action_queue,log_udp_port = 41001):
	if tag == "定点闪（A连点）":
		return BattleShiny(frame,opencv_processed_video_frame,controller_action_queue,log_udp_port)
	else:
		return NoneOpenCV(frame,opencv_processed_video_frame,controller_action_queue,log_udp_port)
		

