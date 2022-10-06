import asyncio
from recognize import frame, opencv

def run(frame_queues,control_queues,video_with,video_height,fps = 5):
	f = frame.Frame(video_with,video_height,fps)
	loop = asyncio.get_event_loop()
	task1 = loop.create_task(f.loop_read(frame_queues[0]))
	task2 = loop.create_task(_task_manager(loop,f,frame_queues[2],control_queues[0],control_queues[1]))
	loop.run_forever()

async def _task_manager(loop,f,opencv_processed_video_frame,opencv_processed_control_queue,controller_action_queue):
	loop = asyncio.get_event_loop()
	task = None
	while True:
		await asyncio.sleep(0.1)
		action = None
		try:
			action = opencv_processed_control_queue.get_nowait()
		except:
			pass
		if not action:
			continue
		if task:
			task.cancel()
			try:
				await task
			except asyncio.CancelledError:
				pass
			task = None
		task = loop.create_task(opencv.create_instance(action,f,opencv_processed_video_frame,controller_action_queue).run())

