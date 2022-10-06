import asyncio
import multiprocessing
import socket
import datatype.device as device

from controller.send_order import OrderSender

_log_udp_port = 41001

def run(dev:device.JoystickDevice,control_queues,log_udp_port=41001):
	global _log_udp_port
	_log_udp_port = log_udp_port
	sender = OrderSender(dev)
	loop = asyncio.get_event_loop()
	task1 = loop.create_task(sender.loop_run(dev))
	task2 = loop.create_task(process_inputs(sender,control_queues[1]))
	task3 = loop.create_task(sender.loop_outputs(send_log))
	loop.run_forever()

async def send_log(data):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(data.encode("utf-8"), ("127.0.0.1", _log_udp_port)) 

async def process_inputs(sender,action_queue:multiprocessing.Queue):
	action = None
	while True:
		while True:
			try:
				action = action_queue.get_nowait()
			except:
				await asyncio.sleep(0.001)
				continue
			break
		msg = action.message
		await sender.add_order(msg.encode("utf-8"))
		if action.type == "realtime" and action.get("realtime") != "action_start" and  action.get("realtime") != "action_stop":
			continue
		await send_log("发送命令：" + msg)