import hid.joystick
import hid.device
device = hid.device.Device_HORIPAD_S
hid.joystick.JoyStickFactory.get_instance(device)


import macros
import time
import customize.task_manager as task_manager
import customize.config as config
import customize.datetime

def main():
    c = config.Config()
    tm = task_manager.TaskManager()
    joystick = hid.joystick.JoyStickFactory.get_instance()
    tm.create_task(joystick.start())
    web_running = False
    tcp_running = False
    try:
        import wifi
        web_running = c.get("web-server.running")
        tcp_running = c.get("tcp-server.running")
    except:
        pass
    web_running = type(web_running) is bool and web_running
    tcp_running = type(tcp_running) is bool and tcp_running
    if web_running or tcp_running:
        import customize.wifi_connect as wifi_connect
        for i in range(1,10):
            try:
                wifi_connect.connect()
                break
            except:
                if i>=5:
                    raise
        print(wifi_connect.ip_address())
        print(wifi.radio.hostname)
        print(customize.datetime.ntpSync())
        if web_running:
            import http_server as http
            tm.create_task(http.serve(), "")
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