#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

EXEC_FILE="rpi_blower_tester"
APP="rpi_blower_app"

SERVICE_FILE=$(ls *.service)
FD_RULES=$(ls *stlinkv2*.rules)

function inst_docker {
  #rootless Docker Installation
  echo "Installing Docker for current user"

  curl -sSL https://get.docker.com | sh
  sudo apt-get install -y uidmap dbus-user-session slirp4netns

  unset DOCKER_HOST
  sudo systemctl disable --now docker.service docker.socket
  sudo rm /var/run/docker.sock

  if ! grep -q "DOCKER_HOST" ~/.bashrc; then
    echo "export DOCKER_HOST=unix://run/user/1000/docker.sock" >> ~/.bashrc
  fi
  source ~/.bashrc

  dockerd-rootless-setuptool.sh install
  sudo loginctl enable-linger $USER
  systemctl --user start docker.service
}

function inst_serv {
  #Systemd Service Installation
  echo "Installing systemd blower service"

  sudo cp $SERVICE_FILE /etc/systemd/system/
  sudo chmod 700 /etc/systemd/system/$SERVICE_FILE
  sudo chgrp root /etc/systemd/system/$SERVICE_FILE 

  sudo cp $SERVICE_FILE /usr/lib/systemd/system/
  sudo chmod 600 /usr/lib/systemd/system/$SERVICE_FILE
  sudo chgrp root /usr/lib/systemd/system/$SERVICE_FILE

  sudo systemctl daemon-reload
}

function cp_udev_rule {
  #STLINK Config
  echo "Setting UDEV rules for STLINK V2"
  sudo cp $FD_RULES /etc/udev/rules.d/
  sudo adduser $USER dialout
}

echo "Beginning installation of "$APP" -- Version: ""$(cat .version)"

sudo apt-get update -y
sudo apt-get install -y git
sudo chmod +x *.sh

inst_docker
inst_serv
cp_udev_rule

sudo chmod +x $EXEC_FILE
sudo cp $EXEC_FILE /usr/local/bin/ 
sudo cp -r blower_tester /usr/local/src/
docker build -t $APP /usr/local/src/blower_tester/

printf "\033[0;32m\nInstallation complete\n\033[0m"
 
if cat /etc/os-release | grep "Raspbian"; then
  echo "RPI detected, enabling on boot"
  sudo systemctl enable $SERVICE_FILE

  echo "Please enable I2C and SPI through raspi-config and reboot"
  echo "'sudo raspi-config' -> Interface Options ..."
fi