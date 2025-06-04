#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR && source .env

#Completely remove the program
sudo rm $BLOWER_INSTALL_DIR/bin/$BLOWER_EXEC_FILE \
        $BLOWER_INSTALL_DIR/src/$BLOWER_PY_APP.env \
        $BLOWER_INSTALL_DIR/man/man1/$BLOWER_EXEC_FILE.1 \
        /etc/systemd/system/$BLOWER_SERVICE_FILE \
        /usr/lib/systemd/system/$BLOWER_SERVICE_FILE \
        /etc/udev/rules.d/49-stlinkv2* 

sudo mandb

sudo rm -r $BLOWER_INSTALL_DIR/src/$BLOWER_PY_APP/ 
sudo systemctl daemon-reload
