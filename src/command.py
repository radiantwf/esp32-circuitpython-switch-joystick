import customize.device_info as device_info
import customize.udp_server as udp_server
import macros


async def process(src_msg: str) -> str:
    ret_msg = None
    msg = src_msg.lower()
    if msg.startswith("gp:"):
        ret_msg = "Done"
    elif msg.startswith("m:"):
        if msg == "m:stop":
            macros.stop()
            ret_msg = "Done"
        else:
            paras = None
            loop = 1
            c = src_msg[2:].split(":")
            if len(c) >= 2:
                try:
                    loop = int(c[1])
                    paras = c[2:]
                except:
                    pass
            await macros.create_task(c[0], loop, paras)
            ret_msg = "Done"
    elif msg == "ram" or msg == "mem":
        ret_msg = "剩余内存:{:.2f}KB".format(device_info.mem_free())
    elif msg == "rom" or msg == "flash":
        rom = device_info.get_rom_info()
        ret_msg = "剩余存储空间:{:.2f}MB/{:.2f}MB".format(rom[0], rom[1])
    return ret_msg


async def on_udp_message(src_msg: str, addr):
    if src_msg == None or src_msg == "":
        return
    for cmd in src_msg.split("|||"):
        ret_msg = await process(cmd)
        if ret_msg != None:
            print("{}\t{}\t\t{}".format(addr, cmd, ret_msg))
            _send_udp_message(ret_msg, addr)


def _send_udp_message(msg: str, addr):
    udp = udp_server.UdpServer()
    udp.send_message(msg, addr)
