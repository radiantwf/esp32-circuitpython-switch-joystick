import macros
import customize.wifi_connect as wifi_connect
import customize.task_manager as task_manager

print("hello hori")


def main():
    wifi_connect.connect()

    import customize.device_info as device_info
    print("剩余内存:{:.2f}KB".format(device_info.mem_free()))
    rom = device_info.get_rom_info()
    print("剩余存储空间:{:.2f}MB/{:.2f}MB".format(rom[0], rom[1]))
    macros.auto_run()
    tm = task_manager.TaskManager()

    import http_server as http
    tm.create_task(http.serve(), "http")

    tm.wait_forever()
    tm.close_loop()


if __name__ == '__main__':
    main()
