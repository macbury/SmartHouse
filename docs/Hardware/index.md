This is the list of all hardware that is present in my smart house.

## Computers

### Gigabyte BRIX GB-BPCE-3455
I needed something more powerfull than RaspberryPi to host all services running my Smart House. [Gigabyte BRIX GB-BPCE-3455](https://www.gigabyte.com/Mini-PcBarebone/GB-BPCE-3455-rev-10#ov) can be extended by normal hard drive and RAM (in my case 8GB RAM and 250GB SSD). The Intel Celeron inside this small box have enought power to even transcode 4K video(plex in docker) and small amount of machine learning.

### Raspberry Pi 3
This small computer is used mainly for DIY stuff like [cat feeder](/DIY/CatFeeder) and [Gateway](/DIY/BluetoothGateway) . First version of my smart house run on one of these, but quickly my requirements outgrown its computing power.


## Z-Wave
My adventure with [Z-Wave](https://www.z-wave.com/) started with [Danfoss Thermostats](https://products.z-wavealliance.org/products/93), after one winter, I received astronomical bill for heating. Interaction with all Z-Wave devices is done using [Aeotec Z-Stick Gen5](https://aeotec.com/z-wave-usb-stick) that is plugged to my Gigabyte BRIX. The cool thing about this setup is that each device is from different manufacturer and they work together. Currently my arsenal of Z-Wave devices consits:

| Device | Quantity | Component | Notes |
| ------------- | :---: | ------------- | ------------- |
| [Aeotec Z-Stick Gen5](https://aeotec.com/z-wave-usb-stick) | 1 | [Z-Wave](https://www.home-assistant.io/components/zwave/) | Main Z-Wave Hub as usb dongle |
| [Danfoss Z-Wave Thermostats](https://products.z-wavealliance.org/products/93) | 3 | [Z-Wave Climate](https://www.home-assistant.io/components/climate.zwave/) | Used for controlling temperature in rooms |
| [NEO Coolcam - Door/Window Sensor](https://shop.zwave.eu/products/sensors/door-window-sensors/1567/neo-coolcam-door/window-sensor) | 5 | [Z-Wave Binary Sensor ](https://www.home-assistant.io/components/binary_sensor.zwave/) | Used for detecting what doors are open/closed |
| [NEO Coolcam - Motion Sensor](https://shop.zwave.eu/detail/index/sArticle/1764) | 2 | [Z-Wave Binary Sensor ](https://www.home-assistant.io/components/binary_sensor.zwave/) | For detecting cat movement and some light automations |
| [NEO Coolcam - Flood Water Leak Alarm Senso](https://www.aliexpress.com/item/NEO-COOLCAM-Z-wave-Flood-Water-Leak-Alarm-Sensor-Water-Leakage-Sensor-Z-wave-Sensor-Alarm/32787289062.html) | 1 | [Z-Wave Binary Sensor](https://www.home-assistant.io/components/binary_sensor.zwave/) | For detecting leakage in bathroom |
| [Fibaro Relay Switch](https://manuals.fibaro.com/relay-switch/) | 8 | [Z-Wave Switch](https://www.home-assistant.io/components/switch.zwave/) | Controling lights and switches |
| [Roller Shutter 3](https://manuals.fibaro.com/roller-shutter-3/) | 1 | [Z-Wave Cover](https://www.home-assistant.io/components/zwave/) | Controling living room blinds |
| [NEO Coolcam - Power Plug](https://www.aliexpress.com/item/NEO-COOLCAM-Z-wave-EU-Smart-Power-Plug-Socket-Home-Automation-Alarm-System-home-Compatible-with/32787926055.html) | 2 | [Z-Wave switch](https://www.home-assistant.io/components/zwave/) | Used for detecting if AGD stuff is working |

## ZigBee

### Philips Hue
I`m using [Philips Hue Hub Gen 2](https://www.amazon.com/gp/product/B014H2P42K/) for controlling my [TRÅDFRI](https://www.ikea.com/us/en/catalog/categories/departments/home_electronics/36812/) lights. The default gateway from Ikea was buggy as hell. After few hours it stopped responding and only fix was to restart it by plugging device from power.

| Device | Quantity | Component |
| ------------- | :---: | ------------- |
| [TRÅDFRI Bulb](https://www.ikea.com/us/en/catalog/products/80339436/) | 2 | [Hue](https://www.home-assistant.io/components/hue/) |

### Xiaomi
Currently most of my sensors is Xiaomi, so I need to use their Gateway to integrate them with Home Assistant. It does intergrate with its ecosystem pretty ok, with support for playing a sound and it also has a rgb led which will change colours on events like upcoming rain, etc. Gateway has blocked access to network(this is still chines company duh.)

| Device | Quantity | Component | Notes |
| ------------- | :---: | ------------- | ------------- |
| [Mi Air Purifier 2](https://www.mi.com/global/air2/) | 1 | [Xiaomi Air Purifier](https://www.home-assistant.io/components/fan.xiaomi_miio/) | Air purifier in bedroom room |
| [Mi Air Purifier 2s](https://www.xiaomistore.pk/mi-air-purifier-2s.html) | 1 | [Xiaomi Air Purifier](https://www.home-assistant.io/components/fan.xiaomi_miio/) | Air purifier in living room |
| [Xiaomi Aqara Hub](https://www.aqara.com/en/smart_hub-product.html) | 1 | [Xiaomi Gateway (Aqara)](https://www.home-assistant.io/components/xiaomi_aqara/) | Used for communication with wirless switches and temperature sensors |
| [Xiaomi Aqara Wireless Remote Switch](https://www.aqara.com/en/86plug.html) | 6 | [Xiaomi Switch](https://www.home-assistant.io/components/switch.xiaomi_aqara/) | These switches are used for triggering various automations |
| [Xiaomi Mijia Roborock Vacuum Cleaner 2](https://xiaomi-mi.co.uk/mi-smart-home/xiaomi-mijia-roborock-robot-vacuum-cleaner-2-white/) | 1 | [Xiaomi Mi Robot Vacuum](https://www.home-assistant.io/components/vacuum.xiaomi_miio/) | Automated to run at specific times based on presence detection. |
| [Xiaomi Mijia Roborock Vacuum Cleaner 2](https://xiaomi-mi.co.uk/mi-smart-home/xiaomi-mijia-roborock-robot-vacuum-cleaner-2-white/) | 1 | [Xiaomi Mi Robot Vacuum](https://www.home-assistant.io/components/vacuum.xiaomi_miio/) | Automated to run at specific times based on presence detection. |
| [Xiaomi Aqara Temperature Humidity Sensor](https://www.amazon.com/OUKU-Xiaomi-Temperature-Humidity-Sensor/dp/B078T7PDTR) | 3 | [Xiaomi Aqara](https://www.home-assistant.io/components/xiaomi_aqara/) | For sampling temperature and humidity in rooms without air purifiers(they have humidity and temperature sensors inside them) |

## Wi-Fi Network
And here are all devices that are connected over Wi-Fi network:

| Device  | Quantity | Connection | Home Assistant | Notes |
| ------------- | :---: | ------------- | ------------- | ------------- |
| [Amazon Echo DOT](https://www.amazon.com/gp/product/B01DFKC2SO) | 3 | WiFi | [Alexa / Amazon Echo](https://www.home-assistant.io/components/alexa/) | The Alexa devices are used as interface to interact with HomeAssistant |
| [Playstation 4](https://www.playstation.com/en-us/explore/ps4/) | 1 | WiFi | [PS4](https://www.home-assistant.io/components/ps4/) | For playing and watching stuff that requires DVD/Blurays |
| [HW-K650 Soundbar w/ Wireless Subwoofer](https://www.samsung.com/us/televisions-home-theater/home-theater/sound-bars/samsung-hw-k650-soundbar-w-wireless-subwoofer-hw-k650-za/) | 1 | WiFi | [ha_samsung_multi_room](https://github.com/macbury/ha_samsung_multi_room) | Some sound goodies control stuff |
| [LG webOS TV 55SK8100PLA](https://www.lg.com/pl/telewizory/lg-55SK8100PLA) | 1 | WiFi | [LG webOS Smart TV ](https://www.home-assistant.io/components/media_player.webostv/) | Watching movies, showing Home Assistant panel and notifications |
| [Netgear Switch GS108GE](https://www.netgear.com/support/product/GS108.aspx) | 1 | Ethernet | - | Asus lyra has only two ethernet ports. |
| [Mesh network router Asus Lyra](https://www.asus.com/us/Networking/Lyra/) | 1 | WiFi | [Asuswrt](https://www.home-assistant.io/components/asuswrt/) | Network, remote access through VPN |
| [QNAP TS-228](https://www.qnap.com/en-us/product/ts-228) | 1 | Ethernet | [QNAP Sensor ](https://www.home-assistant.io/components/sensor.qnap/) | Main storage array for backups, TimeMachine and photos |
| [RIGGAD Lamp](https://www.ikea.com/pl/pl/catalog/products/60385636/) | 1 | Wi-Fi | [MQTT Light](https://www.home-assistant.io/components/light.mqtt/) | Lamp with wirless charging. Additionaly I have replaced default bulb with [NeoPixel Ring](https://www.adafruit.com/product/1463) and [WeMos D1 mini](https://wiki.wemos.cc/products:d1:d1_mini). [See this in action](https://www.youtube.com/watch?v=iVw9GvY-IWI) |
| [Linak Desk](https://www.linak.com/business-areas/desks/office-desks/) | 1 | Bluetooth | [MQTT Cover](https://www.home-assistant.io/components/cover.mqtt/) | Nice desk with ability to adjust height |

## Depracated/Old hardware
| Device  | Quantity | Connection | Home Assistant | Notes |
| ------------- | :---: | ------------- | ------------- | ------------- |
| [Router Asus RT-AC56U](https://www.asus.com/us/Networking/RTAC56U/) | 1 | WiFi | [Asuswrt](https://www.home-assistant.io/components/asuswrt/) | Network, remote access through VPN |