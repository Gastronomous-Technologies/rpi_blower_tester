Testing application for CG5-CHAS-E-19 blower/thermocouple PCBAs

Install: bin/rpi_blower_tester install

Fully Uninstall: 
  sudo rm /usr/local/bin/rpi_blower_tester
  sudo rm -r /usr/local/src/blower_tester/
  sudo rm -r /etc/udev/rules.d/49-stlinkv*
  sudo rm /etc/systemd/system/blower_tester.service
  sudo rm /usr/lib/systemd/system/blower_tester.service
  sudo systemctl daemon-reload
