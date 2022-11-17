import hid.joystick
import hid.device
device = hid.device.Device_Switch_Pro
hid.joystick.JoyStickFactory.get_instance(device)


import macros
import time
import customize.task_manager as task_manager
import customize.config as config

def main():
    c = config.Config()
    tm = task_manager.TaskManager()
    joystick = hid.joystick.JoyStickFactory.get_instance()
    tm.create_task(joystick.start())
    tcp_running = False
    try:
        import wifi
        tcp_running = c.get("tcp-server.running")
    except:
        pass
    tcp_running = type(tcp_running) is bool and tcp_running
    if tcp_running:
        import customize.wifi_connect as wifi_connect
        for i in range(1,10):
            try:
                wifi_connect.connect()
                break
            except:
                if i>=5:
                    raise
        print(wifi_connect.ip_address())
        if tcp_running:
            from tcp_server import TcpServer
            port = 5000
            try:
                port = int(c.get("tcp-server.port"))
            except:
                pass
            if port < 0 or port > 65535:
                port = 5000
            tm.create_task(TcpServer().start_serve(port))
    span = time.monotonic()
    if span < 15:
        time.sleep(15 - span)
    macros.action_queue_task_start()
    macros.auto_run()

    tm.wait_forever()
    tm.close_loop()


if __name__ == '__main__':
    main()
