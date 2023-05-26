#!/bin/bash  

docker run -it --rm --user "$(id -u):$(id -g)" -v "$PWD":/usr/src/app -w /usr/src/app django django-admin.py startproject pioneersite