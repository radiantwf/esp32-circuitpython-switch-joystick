import socketpool
import wifi
import customize.wifi_connect as wifi_connect
import customize.device_info as device_info
import macros
import asyncio
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest

_pool = socketpool.SocketPool(wifi.radio)
_server = HTTPServer(_pool,"/")


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
def ram(request: HTTPRequest):
    with HTTPResponse(request, content_type="text/plain;charset=utf-8") as response:
        response.send("CPU温度: {: .2f}".format(device_info.cpu_temperature()))

@_server.route("/ram", "GET")
def ram(request: HTTPRequest):
    with HTTPResponse(request, content_type="text/plain;charset=utf-8") as response:
        response.send("剩余内存: {: .2f}KB".format(device_info.mem_free()))


@_server.route("/rom", "GET")
def rom(request: HTTPRequest):
    rom = device_info.get_rom_info()
    with HTTPResponse(request, content_type="text/plain;charset=utf-8") as response:
        response.send("剩余存储空间:{:.2f}MB/{:.2f}MB".format(rom[0], rom[1]))


@_server.route("/status", "GET")
def status(request: HTTPRequest):
    txt = ""
    txt += "{}\n\n".format(macros.status_info())
    txt += "CPU温度: {: .2f}\n".format(device_info.cpu_temperature())
    txt += "剩余内存: {: .2f}KB\n".format(device_info.mem_free())
    rom = device_info.get_rom_info()
    txt += "剩余存储空间:{:.2f}MB/{:.2f}MB\n".format(rom[0], rom[1])
    with HTTPResponse(request, content_type="text/plain;charset=utf-8") as response:
        response.send(txt)


@_server.route("/macro/current", "GET")
def macro_current(request: HTTPRequest):
    with HTTPResponse(request, content_type="text/plain;charset=utf-8") as response:
        response.send(macros.current_info())


@_server.route("/macro/result", "GET")
def macro_result(request: HTTPRequest):
    with HTTPResponse(request, content_type="text/plain;charset=utf-8") as response:
        response.send(macros.result_info())


@_server.route("/macro/stop", "GET")
def macro_stop(request: HTTPRequest):
    macros.macro_stop()
    with HTTPResponse(request, content_type="text/plain;charset=utf-8") as response:
        response.send("Done")

@_server.route("/macro/published", "GET")
def marcos(request: HTTPRequest):
    body = macros.published()
    with HTTPResponse(request, content_type="text/plain;charset=utf-8") as response:
        response.send(body)


@_server.route("/macro/start", "POST")
def macro_start(request: HTTPRequest):
    raw_text = request.raw_request.decode("utf8")
    splits = raw_text.split("\n")
    cmd = splits[len(splits) - 1]
    ret = macros.add_joystick_task(cmd)
    with HTTPResponse(request, content_type="text/plain;charset=utf-8") as response:
        response.send(ret)


@_server.route("/")
def index_root(request: HTTPRequest):
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send_file("/web/index.html")

@_server.route("/index.html")
def index(request: HTTPRequest):
    with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
        response.send_file("/web/index.html")

@_server.route("/jquery-3.6.1.min.js")
def js1(request: HTTPRequest):
    with HTTPResponse(request, content_type=MIMEType.TYPE_JS) as response:
        response.send_file("/web/jquery-3.6.1.min.js")