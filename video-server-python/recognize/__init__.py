import asyncio
from recognize import frame
from recognize.opencv.battle_shiny import BattleShiny

def run(frame_queue,opencv_processed_video_frame,dev_joystick,video_with,video_height,fps = 5):
	f = frame.Frame(video_with,video_height,fps)
	loop = asyncio.get_event_loop()
	task1 = loop.create_task(f.loop_read(frame_queue))
	task2 = loop.create_task(BattleShiny(f).run(opencv_processed_video_frame,dev_joystick))
	loop.run_forever()