#!/bin/bash
docker build . -t circuitpython-lolin-s2-mini
docker run -d --rm -v $(PWD)/build:/root/build circuitpython-lolin-s2-mini
