import macros
import customize.udp_server as udp_server
import customize.wifi_connect as wifi_connect
import customize.task_manager as task_manager
import command

print("hello hori")


def main():
    wifi_connect.connect()

    import customize.device_info as device_info
    print("剩余内存:{:.2f}KB".format(device_info.mem_free()))
    rom = device_info.get_rom_info()
    print("剩余存储空间:{:.2f}MB/{:.2f}MB".format(rom[0], rom[1]))
    tm = task_manager.TaskManager()
    tm.create_task(macros.auto_run())

    udp = udp_server.UdpServer()
    udp.on_message = command.on_udp_message

    tm.create_task(udp.start_serve(), "udp")

    tm.wait_forever()
    tm.close_loop()


if __name__ == '__main__':
    main()
