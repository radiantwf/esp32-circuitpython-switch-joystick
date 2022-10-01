#!/bin/bash
python3 -m venv env

source ./env/bin/activate
pip install opencv-python PySide6 ffmpeg-python pyinstaller auto-py-to-exe pillow --index-url http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com


auto-py-to-exe