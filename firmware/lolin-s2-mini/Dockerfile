# https://learn.adafruit.com/building-circuitpython/build-circuitpython
# https://docs.circuitpython.org/en/latest/BUILDING.html
# https://learn.adafruit.com/building-circuitpython/espressif-build
FROM python:3

USER root

RUN apt-get update && apt-get -y install \
	git \
	ninja-build cmake libusb-1.0-0 gettext

WORKDIR /root
# it's taking a long time
RUN git clone -b 7.3.3 --depth=1 https://github.com/adafruit/circuitpython.git && \
	cd circuitpython && \
	make fetch-submodules

WORKDIR /root/circuitpython/ports/espressif
RUN esp-idf/install.sh

WORKDIR /root/circuitpython/ports/espressif/boards
RUN sed -i 's/USB_VID = 0x303A/USB_VID = 0x0F0D/g' lolin_s2_mini/mpconfigboard.mk && \
	sed -i 's/USB_PID = 0x80C3/USB_PID = 0x00C1/g' lolin_s2_mini/mpconfigboard.mk && \
	sed -i 's/USB_PRODUCT = "S2 Mini"/USB_PRODUCT = "HORI CO.,LTD."/g' lolin_s2_mini/mpconfigboard.mk && \
	sed -i 's/USB_MANUFACTURER = "Lolin"/USB_MANUFACTURER = "HORIPAD S"/g' lolin_s2_mini/mpconfigboard.mk

WORKDIR /root/circuitpython/ports/espressif

VOLUME ["/root/build"]

CMD ["/bin/bash", "-c", "source esp-idf/export.sh && make -j$(getconf _NPROCESSORS_ONLN) BOARD=lolin_s2_mini && cp -r build-lolin_s2_mini/* /root/build"]
