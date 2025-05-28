#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SERVICE_FILE=$(cd $SCRIPT_DIR && ls *.service)

#System Updates
sudo apt-get update -y
sudo apt-get install -y git

#Docker Installation
echo "Installing Docker"

curl -sSL https://get.docker.com | sh
sudo apt-get install -y uidmap
sudo systemctl enable docker
sudo systemctl start docker

echo "export PATH=/usr/bin:$PATH" >> ~/.bashrc
echo "export DOCKER_HOST=unix:///run/user/1000/docker.sock" >> ~/.bashrc
source ~/.bashrc

#Systemd Service Installation
echo "Installing systemd blower service"

sudo cp $SCRIPT_DIR/$SERVICE_FILE /etc/systemd/system/ 
sudo cp $SCRIPT_DIR/$SERVICE_FILE /usr/lib/systemd/system/
sudo chmod 700 /etc/systemd/system/$SERVICE_FILE
sudo chmod 600 /usr/lib/systemd/system/$SERVICE_FILE
sudo chgrp root /etc/systemd/system/$SERVICE_FILE /usr/lib/systemd/system/$SERVICE_FILE
sudo chown root /etc/systemd/system/$SERVICE_FILE /usr/lib/systemd/system/$SERVICE_FILE

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_FILE

#STLINK Udev
sudo cp $SCRIPT_DIR/config/49-stlinkv* /etc/udev/rules.d/
