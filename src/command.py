import customize.device_info as device_info
import customize.udp_server as udp_server
import macros


async def on_udp_message(src_msg: str, addr):
    if src_msg == None or src_msg == "":
        return
    msg = src_msg.lower()
    for cmd in msg.split("|||"):
        ret_msg = None
        if cmd.startswith("gp:"):
            ret_msg = "Done"
        elif cmd.startswith("m:"):
            if cmd == "m:stop":
                await macros.stop()
                ret_msg = "Done"
            else:
                loop = 1
                c = src_msg[2:].split(":")
                if len(c) == 2:
                    try:
                        loop = int(c[1])
                    except:
                        pass
                await macros.create_task(c[0], loop)
                ret_msg = "Done"
        elif cmd == "ram" or cmd == "mem":
            ret_msg = "剩余内存:{:.2f}KB".format(device_info.mem_free())
        elif cmd == "rom" or cmd == "flash":
            rom = device_info.get_rom_info()
            ret_msg = "剩余存储空间:{:.2f}MB/{:.2f}MB".format(rom[0], rom[1])
        if ret_msg != None:
            print("{}\t{}\t\t{}".format(addr, cmd, ret_msg))
            _send_message(ret_msg, addr)


def _send_message(msg: str, addr):
    udp = udp_server.UdpServer()
    udp.send_message(msg, addr)
