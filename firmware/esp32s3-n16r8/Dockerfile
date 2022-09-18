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
# https://github.com/adafruit/circuitpython/tree/main/ports/espressif/boards/espressif_esp32s3_devkitc_1_n8r2
RUN cp -r espressif_esp32s3_devkitc_1_n8r2 espressif_esp32s3_devkitc_1_n16r8 && \
	sed -i 's/ESP32-S3-DevKitC-1-N8R2/ESP32-S3-DevKitC-1-N16R8/g' espressif_esp32s3_devkitc_1_n16r8/mpconfigboard.h && \
	sed -i 's/USB_VID = 0x303A/USB_VID = 0x0F0D/g' espressif_esp32s3_devkitc_1_n16r8/mpconfigboard.mk && \
	sed -i 's/USB_PID = 0x7003/USB_PID = 0x00C1/g' espressif_esp32s3_devkitc_1_n16r8/mpconfigboard.mk && \
	sed -i 's/USB_PRODUCT = "ESP32-S3-DevKitC-1-N8R2"/USB_PRODUCT = "HORI CO.,LTD."/g' espressif_esp32s3_devkitc_1_n16r8/mpconfigboard.mk && \
	sed -i 's/USB_MANUFACTURER = "Espressif"/USB_MANUFACTURER = "HORIPAD S"/g' espressif_esp32s3_devkitc_1_n16r8/mpconfigboard.mk && \
	# CIRCUITPY_ESP_FLASH_MODE DIO -> QIO
	sed -i 's/dio/qio/g' espressif_esp32s3_devkitc_1_n16r8/mpconfigboard.mk && \
	# CIRCUITPY_ESP_FLASH_SIZE 8MB -> 16MB
	sed -i 's/8MB/16MB/g' espressif_esp32s3_devkitc_1_n16r8/mpconfigboard.mk && \
	echo 'CIRCUITPY_ESP32_CAMERA = 0' >> espressif_esp32s3_devkitc_1_n16r8/mpconfigboard.mk && \
	#  QUAD -> OCTAL
	sed -i 's/CONFIG_SPIRAM_MODE_QUAD/CONFIG_SPIRAM_MODE_OCT/g' espressif_esp32s3_devkitc_1_n16r8/sdkconfig && \
	# 2MB -> 8MB
	sed -i 's/2097152/8388608/g' espressif_esp32s3_devkitc_1_n16r8/sdkconfig

WORKDIR /root/circuitpython/ports/espressif

VOLUME ["/root/build"]

CMD ["/bin/bash", "-c", "source esp-idf/export.sh && make -j$(getconf _NPROCESSORS_ONLN) BOARD=espressif_esp32s3_devkitc_1_n16r8 && cp -r build-espressif_esp32s3_devkitc_1_n16r8/* /root/build"]
