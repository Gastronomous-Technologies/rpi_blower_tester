## Thermocouple/Blower Production Testing Testing Application
### Supports CG6-CHAS-E-019 V1.5+

### Overview
This is a software package built in bash and python to program and validate
[CG6-CHAS-E-019 V1.5+](https://gastronomous.365.altium.com/designs/DB1DAFDE-615B-4E2D-85D4-2C2DB54074B0#design) boards with a [Blower Thermocouple Tester CG6-TEST-E-019](https://gastronomous.365.altium.com/designs/1A2DD31A-9A23-4A60-B4DA-FE0705F6627D?activeView=SCH&activeDocumentId=RPI.SchDoc&variant=[No+Variations]&location=[1,96.72,14.2,22.42]#design). 

The host machine is a Raspberry Pi 5 B. Programming of the STM32's option bytes on the device under test (DUT) is accomplished using a [STLINKV2](https://www.amazon.ca/CANADUINO-Compatible-Circuit-Programmer-Debugger/dp/B07B2K6ZPK/ref=asc_df_B07B2K6ZPK?mcid=d99c4133b6a134a289509d90224f34ed&tag=googleshopc0c-20&linkCode=df0&hvadid=706724917350&hvpos=&hvnetw=g&hvrand=15777128983881431215&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9192147&hvtargid=pla-836307266791&psc=1&gad_source=1) programmer in conjunction with the opensource [STlink software](https://github.com/stlink-org/stlink?tab=readme-ov-file). Programming of the STM32 is completed over the USB connection using the 
opensource [stm32flash](https://sourceforge.net/p/stm32flash/wiki/Home/) to test the reprogrammability of the PCBAs when installed in the end machine.

### Working Principle
A systemd service starts a docker container that launches a python application on boot. Upon pressing the button the fixture will configure and program the device under test (DUT). Some automated tests will be performed to drive fans, measure thermocouples, etc. and the result will be displayed on the attached monitor. The test fixture loads test-firmware on the device which is later erased. The test firmware holds drives the red activity LED without blinking it as done in production firmware. After all tests are completed the STM32 microcontroller on the device under test will be erased. To trigger a safe shutdown of the host's operating system the operator should press and hold the push to test (PTT) button for a number of seconds.

### API Information
After installation run
```sh
rpi_blower_tester --help
```
or 
```sh
man rpi_blower_tester
```

### OS Support
Program Installation: 64 bit Raspberry Pi OS Lite (64-bit), Deb-Based Linux \
Program Execution: RPI 5 B with CG6-TEST-E-019 PCBA \
\
Python App Installation and Unit Tests: Raspbian, Linux \
Python App Execution: RPI 5 B with CG6-TEST-E-019 PCBA 

## Deployment Instructions
1. Download and install [rpi-imager](https://www.raspberrypi.com/software/)
2. Use rpi-imager with a fresh SD card 16 GB or larger and format with Raspberry Pi OS Lite (64-bit) \
   <img width="500" height="300" alt="image" src="https://github.com/user-attachments/assets/778b28a5-e8dd-417d-ae4b-ab7e75072933" />
3. Apply custom OS settings so that the card automatically connects to Wi-Fi \
   <img width="350" height="500" alt="image" src="https://github.com/user-attachments/assets/446f8cb3-eb5c-4aa8-87de-d2846b9a80df" />
5. Write the image to the card \
   <img width="500" height="300" alt="image" src="https://github.com/user-attachments/assets/b94a9dbd-6a11-4de4-a960-2b3d34832387" />
6. Plug card into RPI 5 B on CG6-TEST-E-019 then connect HDMI to a monitor and plug in power cable
7. After the RPI 5 B boots and resizes the file system (this may take a few minutes) log in as a non-root user
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
