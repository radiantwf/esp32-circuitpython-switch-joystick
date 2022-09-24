import macros
import time
import customize.wifi_connect as wifi_connect
import customize.task_manager as task_manager
import customize.config as config

print("hello hori")


def main():
    c = config.Config()
    web_runing = c.get("web-server.running")
    tm = task_manager.TaskManager()
    if type(web_runing) is bool and web_runing:
        wifi_connect.connect()
        import http_server as http
        tm.create_task(http.serve(), "http")
    
    span = time.monotonic()
    if span < 15:
        time.sleep(15 - span)
    macros.auto_run()

    tm.wait_forever()
    tm.close_loop()


if __name__ == '__main__':
    main()

