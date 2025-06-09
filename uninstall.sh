#!/bin/bash
#Should be run as root

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR && source .env

#Completely remove the program
rm $BLOWER_INSTALL_DIR/bin/$BLOWER_EXEC_FILE \
   $BLOWER_INSTALL_DIR/src/$BLOWER_PY_APP.env \
   $BLOWER_INSTALL_DIR/man/man1/$BLOWER_EXEC_FILE.1 \
   /etc/systemd/system/$BLOWER_SERVICE_FILE \
   /usr/lib/systemd/system/$BLOWER_SERVICE_FILE \
   /etc/udev/rules.d/49-stlinkv2*

mandb

rm -r $BLOWER_INSTALL_DIR/src/$BLOWER_PY_APP/ 
systemctl daemon-reload
