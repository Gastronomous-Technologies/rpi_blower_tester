#!/bin/bash 
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd $SCRIPT_DIR/../
docker run --rm -it -v /dev:/dev --device /dev:/dev --net=host -it blower_app
