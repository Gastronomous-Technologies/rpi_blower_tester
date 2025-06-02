## Thermocouple/Blower Production Testing Testing Application
### Supports CG5-CHAS-E-19 V2.1+

### Overview
This is a software package built in bash and python to program and validate
[CG5-ELEC-E-019 V2.1+](https://gastronomous.365.altium.com/designs/42E0F161-9A46-4870-873C-406A7E8BF709#design) boards with a [Blower Thermocouple Tester CG5-TEST-E-019](https://gastronomous.365.altium.com/designs/2D430438-1214-45B7-B8A9-F794314B5EE8?activeDocumentId=RPI_ZERO.SchDoc&variant=[No+Variations]&activeView=SCH&location=[1,96.74,17.35,27.39]#design). 

The host machine is a Raspberry Pi Zero 2W. Programming of the device under test (DUT) is accomplished using a [STLINKV2](https://www.amazon.ca/CANADUINO-Compatible-Circuit-Programmer-Debugger/dp/B07B2K6ZPK/ref=asc_df_B07B2K6ZPK?mcid=d99c4133b6a134a289509d90224f34ed&tag=googleshopc0c-20&linkCode=df0&hvadid=706724917350&hvpos=&hvnetw=g&hvrand=15777128983881431215&hvpone=&hvptwo=&hvqmt=&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=9192147&hvtargid=pla-836307266791&psc=1&gad_source=1)  programmer in conjunction with the opensource [STlink software](https://github.com/stlink-org/stlink?tab=readme-ov-file). 

### Working Principle
A systemd service starts a docker container that launches a python application. The python application will prompt the user to complete some operations and input y/n feedback and then the stlink will program the DUT to complete some tests, check the thermocouples, drive the fans, etc. This isn't yet completed.

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
Raspbian, Deb-Based Linux

## Install
```sh
sudo chmod +x install.sh && ./install.sh
```

## Uninstall
```sh
./uninstall.sh
```
