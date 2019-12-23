## Wemos D1 to ESPHome Pin Mapping

```C
static const uint8_t D0   = 16;
static const uint8_t D1   = 5;
static const uint8_t D2   = 4;
static const uint8_t D3   = 0;
static const uint8_t D4   = 2;
static const uint8_t D5   = 14;
static const uint8_t D6   = 12;
static const uint8_t D7   = 13;
static const uint8_t D8   = 15;
static const uint8_t RX   = 3;
static const uint8_t TX   = 1;
```

https://github.com/esp8266/Arduino/blob/master/variants/d1_mini/pins_arduino.h#L37

## How to add new device

Visit web ui under http://192.168.1.12:6052. Go through the creator proces. After that you should see new item in the dashboard. Hit compile, wait for whole process to finish. You should see download button. Click it and download *.bin file. Then using https://github.com/esphome/esphome-flasher burn it to the ESP. Now next upload should be done OTA.