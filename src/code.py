import macros
import customize.wifi_connect as wifi_connect
import customize.task_manager as task_manager

print("hello hori")


def main():
    wifi_connect.connect()

    
    macros.auto_run()
    tm = task_manager.TaskManager()

    import http_server as http
    tm.create_task(http.serve(), "http")

    tm.wait_forever()
    tm.close_loop()


if __name__ == '__main__':
    main()

