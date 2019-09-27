## Automations
There are some limitations with HomeAssistant YAML configuration files. I wanted to add more sophisticated logic, and my YAML file become  unreadable cluster fuck, thankfully there is a nifty tool called [AppDaemon](https://github.com/home-assistant/appdaemon) that allowed me to implement these automations in python.

### Air Purifier
Xiaomi Air Purifier has big fallacy. It detect water vapor from humidifier as pollution and quickly increases AQI. These causes feedback loop and Air purifier goes super sayian mode and sets fan spin to over 9000. To combat this problem automation changes purifier mode to favorite with speed level that equals 1. Also air purifier should stop working when balcone door or window is opened. And finnaly the schedule is controlled by calendar entity and of cource it is also based on presence in the home.  

```yaml
living_room_air:
  module: air_purifier_ai
  class: AirPurifierAI
  alt_mode_entity: switch.living_room_humidifier
  alt_mode: 'Favorite'
  alt_mode_speed: 1
  calendar: calendar.oczyszczacz_salon
  fan_id: 'fan.living_room_air_purifier'
  family_devices: 'group.family'
  fallback: 5400
  mode: 'Auto'
  balcone_door: sensor.living_room_balcone_door
```

### Adaptive Room Heating
My apartament is in block from 1960. Some of inside installation is pretty ancient. For example my heating radiator has a dial with range 1 to 5 but really heat going throug when is set to 5, and anything below that probabbly depends on combined pressure from all apartaments below(or it is caused by lepricons). 

__TODO: Write more about this__

### Baterry report
[This](https://github.com/macbury/SmartHouse/blob/master/appdaemon/apps/battery.py) automation checks everyday at 6PM if there are devices with low battery level and sends notification.

### Humidifier

__TODO: Write more about this__

### Spotify Light

__TODO: Write more about this__