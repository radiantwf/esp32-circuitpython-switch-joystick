#!/bin/bash
docker build . -t circuitpython
docker run -d --rm -v $(PWD)/build:/root/build circuitpython
