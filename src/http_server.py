import socketpool
import wifi
import customize.wifi_connect as wifi_connect
import customize.device_info as device_info
import macros
import asyncio
from adafruit_httpserver.response import Response,FileResponse
from adafruit_httpserver.server import Server
from adafruit_httpserver.mime_types import MIMETypes
from adafruit_httpserver.request import Request

MIMETypes.configure(
    default_to="text/plain",
    keep_for=[".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".ico"],
)

_pool = socketpool.SocketPool(wifi.radio)
_server = Server(_pool,"/")


async def serve():
    global _server
    HOST = str(wifi_connect.ip_address())
    print(HOST)
    _server.start(HOST)

    while True:
        try:
            _server.poll()
            await asyncio.sleep_ms(50)
        except OSError:
            continue


@_server.route("/cpu", "GET")
def ram(request: Request):
    return Response(request, content_type="text/plain;charset=utf-8",body="CPU温度: {: .2f}".format(device_info.cpu_temperature()))

@_server.route("/ram", "GET")
def ram(request: Request):
    return Response(request, content_type="text/plain;charset=utf-8",body="剩余内存: {: .2f}KB".format(device_info.mem_free()))

@_server.route("/rom", "GET")
def rom(request: Request):
    rom = device_info.get_rom_info()
    return Response(request, content_type="text/plain;charset=utf-8",body="剩余存储空间:{:.2f}MB/{:.2f}MB".format(rom[0], rom[1]))


@_server.route("/status", "GET")
def status(request: Request):
    txt = ""
    txt += "{}\n\n".format(macros.status_info())
    txt += "CPU温度: {: .2f}\n".format(device_info.cpu_temperature())
    txt += "剩余内存: {: .2f}KB\n".format(device_info.mem_free())
    rom = device_info.get_rom_info()
    txt += "剩余存储空间:{:.2f}MB/{:.2f}MB\n".format(rom[0], rom[1])
    return Response(request, content_type="text/plain;charset=utf-8",body=txt)


@_server.route("/macro/current", "GET")
def macro_current(request: Request):
    return Response(request, content_type="text/plain;charset=utf-8",body=macros.current_info())


@_server.route("/macro/result", "GET")
def macro_result(request: Request):
    return Response(request, content_type="text/plain;charset=utf-8",body=macros.result_info())


@_server.route("/macro/stop", "GET")
def macro_stop(request: Request):
    macros.macro_stop()
    return Response(request, content_type="text/plain;charset=utf-8",body="Done")

@_server.route("/macro/published", "GET")
def marcos(request: Request):
    body = macros.published()
    return Response(request, content_type="text/plain;charset=utf-8",body=body)

@_server.route("/macro/start", "POST")
def macro_start(request: Request):
    raw_text = request.raw_request.decode("utf8")
    splits = raw_text.split("\n")
    cmd = splits[len(splits) - 1]
    ret = macros.add_joystick_task(cmd)
    return Response(request, content_type="text/plain;charset=utf-8",body=ret)

@_server.route("/")
def index_root(request: Request):
    return FileResponse(request, filename='index.html', root_path='/web')

@_server.route("/index.html")
def index(request: Request):
    return FileResponse(request, filename='index.html', root_path='/web')

@_server.route("/jquery-3.6.1.min.js")
def js1(request: Request):
    return FileResponse(request, filename='jquery-3.6.1.min.js', root_path='/web')
