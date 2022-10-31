#!/bin/bash
docker build --network host --build-arg http_proxy=http://192.168.50.2:10087 --build-arg https_proxy=http://192.168.50.2:10087 . -t circuitpython-lolin-s2-mini
docker run -d --env http_proxy=http://192.168.50.2:10087 --env https_proxy=http://192.168.50.2:10087 --rm -v $(PWD)/build:/root/build circuitpython-lolin-s2-mini
# docker run -it --env http_proxy=http://192.168.50.2:10087 --env https_proxy=http://192.168.50.2:10087 -v E:\workspace\pokemon\esp32-pokemon\firmware\lolin-s2-mini\switch_pro\build:/root/build circuitpython-lolin-s2-mini /bin/bash
