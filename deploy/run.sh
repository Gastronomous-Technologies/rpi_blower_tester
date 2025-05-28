#!/bin/bash 
docker run -it -v /dev:/dev --device /dev:/dev --net=host -it blower_app
