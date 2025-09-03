## Thermocouple/Blower Production Testing Testing Application
### Supports CG5-CHAS-E-19 V2.1+

### Overview
This is a software package built in bash and python to program and validate
[CG5-ELEC-E-019 V2.1+](https://gastronomous.365.altium.com/designs/42E0F161-9A46-4870-873C-406A7E8BF709#design) boards with a [Blower Thermocouple Tester CG5-TEST-E-019](https://gastronomous.365.altium.com/designs/2D430438-1214-45B7-B8A9-F794314B5EE8?activeDocumentId=RPI_ZERO.SchDoc&variant=[No+Variations]&activeView=SCH&location=[1,96.74,17.35,27.39]#design). 

The host machine is a Raspberry Pi Zero 2W. Programming of the device under test (DUT) is accomplished using a [STLINKV2](https://www.amazon.ca/CANADUINO-Compatible-Circuit-Programmer-Debugger/dp/B07B2K6ZPK/ref=asc_df_B07B2K6ZPK?mcid=d99c4133b6a134a289509d90224f34ed&tag=googleshopc0c-20&linkCode=df0&hvadid=706724917350&hvpos=&hvnetw=g&hvrand=15777128983881431215&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9192147&hvtargid=pla-836307266791&psc=1&gad_source=1)  programmer in conjunction with the opensource [STlink software](https://github.com/stlink-org/stlink?tab=readme-ov-file). 

### Working Principle
A systemd service starts a docker container that launches a python application. The python application will prompt the user to complete some operations and input y/n feedback and then the stlink will program the DUT to complete some tests, check the thermocouples, drive the fans, etc. 

### API Information
After installation run
```sh
rpi_blower_app --help
```
or 
```sh
man rpi_blower_app
```

### OS Support
Program Installation: 64 bit Raspberry Pi OS Lite (64-bit), Deb-Based Linux \
Program Execution: RPI Zero 2 W with CG5-TEST-E-019 PCBA \
\
Python App Installation and Unit Tests: Raspbian, Linux, Windows \
Python App Execution: RPI Zero 2 W with CG5-TEST-E-019 PCBA 

## Deployment Instructions
1. Download and install [rpi-imager](https://www.raspberrypi.com/software/)
2. Use rpi-imager with a fresh SD card 16 GB or larger and format with Raspberry Pi OS Lite (64-bit) \
   <img width="500" height="300" alt="image" src="https://github.com/user-attachments/assets/386b40bd-7f5b-4315-a732-86e005b8f8eb" />
3. Apply custom OS settings so that the card automatically connects to Wi-Fi \
   <img width="250" height="500" alt="image" src="https://github.com/user-attachments/assets/446f8cb3-eb5c-4aa8-87de-d2846b9a80df" />
5. Write the image to the card \
   <img width="500" height="300" alt="image" src="https://github.com/user-attachments/assets/a348bae7-b2cb-4fbd-b59b-b07764554d9f" />
6. Plug card into RPI Zero 2 W on CG5-TEST-E-019 then connect HDMI to a monitor and plug in power cable
7. After the RPI Zero 2 W boots and resizes the file system (this may take a few minutes) log in as a non-root user
8. Copy over the zip or tar of the release to the device. Do not clone repositories on the disk if sending the device externally \
   Hint: if using a flash drive you need to mount the drive.
   ```
   mkdir ~/usb
   lsblk #find the USB's partition name, ex: /dev/sda1
   sudo mount <partition name> ~/usb
   cp ~/usb/rpi* ~
   sudo umount -l ~/usb #Now safe to remove drive
   sudo chown $USER -R ~/rpi_blower_tester* && sudo chgrp $USER -R ~/rpi_blower_tester*
   unzip rpi_blower_tester* #then cd into directory
   ```
8. Install the program as shown below 

## Install
```sh
sudo ./install.sh
sudo reboot
```

## Uninstall
```sh
sudo ./uninstall.sh
```
