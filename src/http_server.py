import socketpool
import wifi
import customize.wifi_connect as wifi_connect
import customize.device_info as device_info
import macros
import asyncio

from adafruit_httpserver import HTTPServer, HTTPResponse


_pool = socketpool.SocketPool(wifi.radio)
_server = HTTPServer(_pool)


async def serve():
    global _server
    HOST = str(wifi_connect.ip_address())
    _server.start(HOST)

    while True:
        try:
            _server.poll()
            await asyncio.sleep_ms(10)
        except OSError:
            continue


@_server.route("/ram", "GET")
def base(request):
    return HTTPResponse(content_type="text/plain;charset=utf-8",
                        body="剩余内存: {: .2f}KB".format(device_info.mem_free()))


@_server.route("/rom", "GET")
def base(request):
    rom = device_info.get_rom_info()
    return HTTPResponse(content_type="text/plain;charset=utf-8",
                        body="剩余存储空间:{:.2f}MB/{:.2f}MB".format(rom[0], rom[1]))


@_server.route("/status", "GET")
def base(request):
    txt = ""
    txt += "{}\n\n".format(macros.status_info())
    txt += "剩余内存: {: .2f}KB\n".format(device_info.mem_free())
    rom = device_info.get_rom_info()
    txt += "剩余存储空间:{:.2f}MB/{:.2f}MB\n".format(rom[0], rom[1])
    return HTTPResponse(content_type="text/plain;charset=utf-8",
                        body=txt)


@_server.route("/macro/current", "GET")
def base(request):
    return HTTPResponse(content_type="text/plain;charset=utf-8",
                        body=macros.current_info())


@_server.route("/macro/result", "GET")
def base(request):
    return HTTPResponse(content_type="text/plain;charset=utf-8",
                        body=macros.result_info())


@_server.route("/macro/stop", "GET")
def base(request):
    macros.stop()
    return HTTPResponse(content_type="text/plain;charset=utf-8",
                        body="Done")


@_server.route("/macro/start", "POST")
def base(request):
    raw_text = request.raw_request.decode("utf8")
    splits = raw_text.split("\n")
    cmd = splits[len(splits) - 1]
    ret = macros.create_task(cmd)
    return HTTPResponse(content_type="text/plain;charset=utf-8", body=ret)
