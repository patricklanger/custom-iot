## Pricision Farming using IoT Nodes, RIOT and WoTPy
### A basic Web of Things Example

This Project was creates in the Module "Advanced Internet/IoT Technologies" at HAW Hamburg. 
It shows some basics in usage of a Thing Discription and how it could be used for Pricision Farming.
You will find the project presentation [here](https://docs.google.com/presentation/d/1-MQOFQoVDG1RkEbfOPX3A7B9lOJ8a6SeKt_77exqNFY/edit?usp=sharing).

#### Contributors
- Isabell Egloff
- Patrick Langer 

#### Required Hardware
- Raspberry Pi
- Board: pba-d-01-kw2x

### Run the project

#### Connect your Pi with ssh
- e.g. `ssh pi@iot-raspi-2.lan`

#### Setup your Raspberry Pi
- Erzeugen eines LoWPAN interface:
		`sudo iwpan phy phy0 set channel 0 22`
		`sudo iwpan dev wpan0 set pan_id 0x23`
		`sudo ip link add link wpan0 name lowpan0 type lowpan`
		`sudo ip link set wpan0 up`
		`sudo ip link set lowpan0 up`
- Config the router advertisement daemon: `sudo vim /etc/radvd.conf` [help](https://linux.die.net/man/5/radvd.conf)
    - define your abro address 
- to run the service: `systemctl start radvd` 
- Abro-Adresse aus radvd.conf hinzufügen: `sudo ip addr add 2001:67c:254:b0b2:affe:2000::1/84 dev lowpan0`

#### Clone the Project
- `git clone ...`
- `cd custom-iot`
- `git submodule init`
- `git submodule update`

#### Start the Resource Directory
- on your Pi run `aiocoap-rd`

#### Start your IoT Device
- the IoT-board must be connected to the Pi
- on Pi gi to the repo main folder `cd custom-iot`
- and flash your board: `BOARD=pba-d-01-kw2x make all flash term`
- your bord shuld connect automaticly

#### Start the Webserver
- on your Pi go to directory `cd custom-iot/Frontend`
- and start the server with `python main.py`
- the console log will show where you will find the web interface


### Additional

#### Links
- [W3C - WoT Description mit Example TD](https://www.w3.org/TR/wot-thing-description/)
- [W3C - Web oft Things](https://www.w3.org/WoT/developers/#runtime-consume)
- [WoTPy - TD Example](https://github.com/agmangas/wot-py/blob/cec61d4bfcddb6287fbb4ed01b0dda218f93ab05/tests/td_examples.py)
- [WoTPy - Doku](https://agmangas.github.io/wot-py/index.html)

#### IoT-Board Overview

| Device                 | ID                                                                                                                                                                  | Supported | Comments                                              |     |     |     |     |
|:---------------------- |:------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:--------- |:----------------------------------------------------- | --- | --- | --- | --- |
| MCU                    | [MKW22D512](http://www.freescale.com/webapp/sps/site/prod_summary.jsp?code=KW2x)                                                                                    | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2265) |     |     |     |     |
| phyWAVE board support  | [phyWAVE](http://www.phytec.de/de/produkte/internet-of-things/phywave.html)                                                                                         | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2059) |     |     |     |     |
| Low-level driver       | GPIO                                                                                                                                                                | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2265) |     |     |     |     |
|                        | PWM                                                                                                                                                                 | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2265) |     |     |     |     |
|                        | UART                                                                                                                                                                | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2265) |     |     |     |     |
|                        | I2C                                                                                                                                                                 | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2265) |     |     |     |     |
|                        | SPI                                                                                                                                                                 | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2265) |     |     |     |     |
|                        | USB-Device                                                                                                                                                          | yes       | [WIP](https://github.com/RIOT-OS/RIOT/pull/3890)      |     |     |     |     |
|                        | RTT                                                                                                                                                                 | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2265) |     |     |     |     |
|                        | RNG                                                                                                                                                                 | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2265) |     |     |     |     |
|                        | Timer                                                                                                                                                               | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2265) |     |     |     |     |
| Radio Chip             | integrated                                                                                                                                                          | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2756) |     |     |     |     |
| Humidity Sensor        | [HDC1000](http://www.ti.com/lit/ds/symlink/hdc1000.pdf)                                                                                                             | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2070) |     |     |     |     |
| Pressure Sensor        | [MPL3115A2](http://www.nxp.com/products/sensors/pressure-sensors/barometric-pressure-15-to-115-kpa/20-to-110kpa-absolute-digital-pressure-sensor:MPL3115A2?)        | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2123) |     |     |     |     |
| Tri-axis Accelerometer | [MMA8652FC](http://www.nxp.com/products/sensors/accelerometers/3-axis-accelerometers/2g-4g-8g-low-g-12-bit-digital-accelerometer:MMA8652FC)                         | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2119) |     |     |     |     |
| Magnetometer           | [MAG3110FCR1](http://www.nxp.com/products/sensors/magnetometers/sample-data-sets-for-inertial-and-magnetic-sensors/freescale-high-accuracy-3d-magnetometer:MAG3110) | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2121) |     |     |     |     |
| Light Sensor           | [TCS3772](https://ams.com/jpn/content/download/291143/1065677/file/TCS3772_Datasheet_EN_v1.pdf)                                                                     | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/3135) |     |     |     |     |
| IR-Termopile Sensor    | [TMP006](http://www.ti.com/product/TMP006)                                                                                                                          | yes       | [mainline](https://github.com/RIOT-OS/RIOT/pull/2148) |     |     |     |     |
| Capacitive Button      | PCB                                                                                                                                                                 | no        | planned                                               |     |     |     |     |
|                        |                                                                                                                                  
