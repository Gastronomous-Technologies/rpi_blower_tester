#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

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

  . ~/.bashrc

  dockerd-rootless-setuptool.sh install
  docker context use rootless
  sudo loginctl enable-linger $USER
  systemctl --user start docker.service
  sudo usermod -aG docker $USER
}

function inst_serv {
  #Systemd Service Installation
  echo "Installing systemd blower service"

  sudo cp $BLOWER_SERVICE_FILE /etc/systemd/system/

  sudo sed -i -e "s|INSTALL_DIR|${BLOWER_INSTALL_DIR::-1}|g" /etc/systemd/system/$BLOWER_SERVICE_FILE
  sudo sed -i -e "s|PROGRAM_NAME|$BLOWER_EXEC_FILE|g" /etc/systemd/system/$BLOWER_SERVICE_FILE
  sudo sed -i -e "s|BLOWER_USER|$USER|g" /etc/systemd/system/$BLOWER_SERVICE_FILE

  sudo chmod 700 /etc/systemd/system/$BLOWER_SERVICE_FILE
  sudo chgrp root /etc/systemd/system/$BLOWER_SERVICE_FILE 

  sudo cp /etc/systemd/system/$BLOWER_SERVICE_FILE /usr/lib/systemd/system/
  sudo chmod 600 /usr/lib/systemd/system/$BLOWER_SERVICE_FILE

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
  sudo mkdir -p $BLOWER_INSTALL_DIR/bin $BLOWER_INSTALL_DIR/src $BLOWER_INSTALL_DIR/share/man/man1

  sudo cp $BLOWER_EXEC_FILE $BLOWER_INSTALL_DIR/bin/ 
  sudo sed -i -e "s|INSTALL_DIR|$BLOWER_INSTALL_DIR|g" $BLOWER_INSTALL_DIR/bin/$BLOWER_EXEC_FILE
  sudo cp -r $BLOWER_PY_APP $BLOWER_INSTALL_DIR/src/

  sudo cp man.1 $BLOWER_INSTALL_DIR/man/man1/$BLOWER_EXEC_FILE.1
  sudo sed -i -e "s/PROG_NAME/"$BLOWER_EXEC_FILE"/g" $BLOWER_INSTALL_DIR/share/man/man1/$BLOWER_EXEC_FILE.1
  sudo mandb

  sudo cp .env $BLOWER_INSTALL_DIR/src/$BLOWER_PY_APP.env

  docker build -t $BLOWER_APP_NAME $BLOWER_INSTALL_DIR/src/$BLOWER_PY_APP/

  printf "\033[0;32m\nInstallation complete\n\033[0m"

  if cat /sys/firmware/devicetree/base/model || grep "Raspberry Pi Zero 2 W"; then
    echo " detected, enabling on boot and setting up hardware peripherals"

    sudo systemctl enable $BLOWER_SERVICE_FILE

    if ! grep -q "video=HDMI-A-1:" /boot/firmware/cmdline.txt; then
      sudo sed -i '1s/^/video=HDMI-A-1:1280x720M@60 /' /boot/firmware/cmdline.txt
    fi

    sudo sed -i -e 's/#dtparam=i2c_arm=on/dtparam=i2c_arm=on/g' /boot/firmware/config.txt
    sudo sed -i -e 's/#dtparam=spi=on/dtparam=spi=on/g' /boot/firmware/config.txt

    sudo sed -i -e 's/660/666/g' /etc/udev/rules.d/99-com.rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger

    printf  "Please reboot Raspberry Pi for changes to take effect\n"
  fi

}

install_main
