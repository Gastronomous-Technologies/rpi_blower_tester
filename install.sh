#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

SERVICE_FILE=$(ls *.service)
FD_RULES=$(ls *stlinkv2*.rules)

function inst_docker {
  #Docker Installation
  if command -v docker; then

    # Allowing packages to be found to ensure rootless installation
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update
    sudo apt-get install docker-ce-rootless-extras -y 

  else
    echo "Installing Docker"
    curl -sSL https://get.docker.com | sh
  fi

  #Allowing rootless
  echo "Allowing rootless docker"
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

function install_main {
  source .env

  echo "Beginning installation of "$BLOWER_APP_NAME" -- Version: "$BLOWER_APP_VERSION")"

  sudo apt-get update 
  sudo apt-get install -y git ca-certificates curl
  sudo chmod +x *.sh

  inst_docker
  inst_serv
  cp_udev_rule

  sudo chmod +x $BLOWER_EXEC_FILE
  sudo cp $BLOWER_EXEC_FILE $BLOWER_INSTALL_DIR/bin/ 
  sudo cp -r $BLOWER_PY_APP $BLOWER_INSTALL_DIR/src/
  sudo cp .env $BLOWER_INSTALL_DIR/src/$BLOWER_PY_APP.env

  docker build -t $BLOWER_APP_NAME $BLOWER_INSTALL_DIR/src/$BLOWER_PY_APP/

  printf "\033[0;32m\nInstallation complete\n\033[0m"
  
  if cat /etc/os-release | grep "Raspbian"; then
    echo "RPI detected, enabling on boot"
    sudo systemctl enable $SERVICE_FILE

    echo "Please enable I2C and SPI through raspi-config and reboot"
    echo "'sudo raspi-config' -> Interface Options ..."
  fi

}

install_main