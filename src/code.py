import macros
import time
import customize.wifi_connect as wifi_connect
import customize.task_manager as task_manager
import customize.config as config

print("hello hori")


def main():
    c = config.Config()
    web_running = c.get("web-server.running")
    tcp_running = c.get("tcp-server.running")
    tm = task_manager.TaskManager()
    web_running = type(web_running) is bool and web_running
    tcp_running = type(tcp_running) is bool and tcp_running
    if web_running or tcp_running:
        for i in range(1,10):
            try:
                wifi_connect.connect()
                break
            except:
                if i>=5:
                    raise
        print(wifi_connect.ip_address())
        if web_running:
            import http_server as http
            tm.create_task(http.serve(), "http")
        if tcp_running:
            from tcp_server import TcpServer
            port = 5000
            try:
                port = int(c.get("tcp-server.port"))
            except:
                pass
            if port < 0 or port > 65535:
                port = 5000
            tm.create_task(TcpServer().start_serve(port), "http")
    span = time.monotonic()
    if span < 15:
        time.sleep(15 - span)
    macros.action_queue_task_start()
    macros.auto_run()

    tm.wait_forever()
    tm.close_loop()


if __name__ == '__main__':
    main()