#!/bin/bash

#Completely remove the program
sudo rm /usr/local/bin/rpi_blower_tester \
        /etc/systemd/system/blower_tester.service \
        /usr/lib/systemd/system/blower_tester.service

sudo rm -r /usr/local/src/blower_tester/ \
           /etc/udev/rules.d/49-stlink* 

sudo systemctl daemon-reload
