#!/bin/bash
#Script must be run as root user

if [ $USER != "root" ]; then
    echo "Script must be run as root user, current user: $USER"
    echo "Exiting..."
    exit 1
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

FD_RULES=$(ls *stlinkv2*.rules)

function inst_docker {
  #Docker Installation
  if command -v docker; then

    # Allowing packages to be found to ensure rootless installation
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc

  else
    echo "Installing Docker"
    curl -sSL https://get.docker.com | sh
  fi

}

function inst_serv {
  #Systemd Service Installation
  echo "Installing systemd blower service"

  cp $BLOWER_SERVICE_FILE /etc/systemd/system/

  sed -i -e "s|INSTALL_DIR|${BLOWER_INSTALL_DIR::-1}|g" /etc/systemd/system/$BLOWER_SERVICE_FILE
  sed -i -e "s|PROGRAM_NAME|$BLOWER_EXEC_FILE|g" /etc/systemd/system/$BLOWER_SERVICE_FILE

  chmod 700 /etc/systemd/system/$BLOWER_SERVICE_FILE
  chgrp root /etc/systemd/system/$BLOWER_SERVICE_FILE

  cp /etc/systemd/system/$BLOWER_SERVICE_FILE /usr/lib/systemd/system/
  chmod 600 /usr/lib/systemd/system/$BLOWER_SERVICE_FILE

  systemctl daemon-reload
}

function cp_udev_rule {
  #STLINK Config
  echo "Setting UDEV rules for STLINK V2"
  cp $FD_RULES /etc/udev/rules.d/
  adduser $USER dialout
}

function install_main {
  . .env

  echo "Beginning installation of "$BLOWER_APP_NAME" -- Version: "$BLOWER_APP_VERSION""

  apt-get update
  apt-get install -y git ca-certificates curl

  inst_docker
  inst_serv
  cp_udev_rule

  chmod +x $BLOWER_EXEC_FILE
  mkdir -p $BLOWER_INSTALL_DIR/bin $BLOWER_INSTALL_DIR/src $BLOWER_INSTALL_DIR/share/man/man1

  cp $BLOWER_EXEC_FILE $BLOWER_INSTALL_DIR/bin/
  sed -i -e "s|INSTALL_DIR|${BLOWER_INSTALL_DIR::-1}|g" $BLOWER_INSTALL_DIR/bin/$BLOWER_EXEC_FILE
  cp -r $BLOWER_PY_APP $BLOWER_INSTALL_DIR/src/

  cp man.1 $BLOWER_INSTALL_DIR/man/man1/$BLOWER_EXEC_FILE.1
  sed -i -e "s/PROG_NAME/"$BLOWER_EXEC_FILE"/g" $BLOWER_INSTALL_DIR/share/man/man1/$BLOWER_EXEC_FILE.1
  mandb

  cp .env $BLOWER_INSTALL_DIR/src/$BLOWER_PY_APP.env

  docker build -t $BLOWER_APP_NAME $BLOWER_INSTALL_DIR/src/$BLOWER_PY_APP/

  printf "\033[0;32m\nInstallation complete\n\033[0m"

  if cat /sys/firmware/devicetree/base/model || grep "Raspberry Pi Zero 2 W"; then
    echo " detected, enabling on boot and setting up hardware peripherals"

    systemctl enable $BLOWER_SERVICE_FILE

    if ! grep -q "video=HDMI-A-1:" /boot/firmware/cmdline.txt; then
      sed -i '1s/^/video=HDMI-A-1:1280x720M@60 /' /boot/firmware/cmdline.txt
    fi

    #SPI enable
    sed -i -e 's/#dtparam=spi/dtparam=spi/g' /boot/firmware/config.txt
    sed -i -e 's/dtparam=spi=off/dtparam=spi=on/g' /boot/firmware/config.txt

    #I2C enable
    sed -i -e 's/#dtparam=i2c_arm/dtparam=i2c_arm/g' /boot/firmware/config.txt
    sed -i -e 's/dtparam=i2c_arm=off/dtparam=i2c_arm=on/g' /boot/firmware/config.txt

    if ! grep -q "^i2c[-_]dev" /etc/modules; then
        printf "i2c-dev\n" >> /etc/modules
    fi
    modprobe i2c-dev

    printf  "Please reboot Raspberry Pi for changes to take effect\n"
  fi

}

install_main
