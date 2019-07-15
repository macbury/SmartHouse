## My Components
Here are components developed by me.

### It will rain

This simple sensor just checks forecast for next few hours, and switches on if there is chance of rain. I use this with simple automation, to notify about next rain by switching blue light:

```yaml
- alias: Switch on blue light alert if it is going to rain
  trigger:
    platform: state
    entity_id: sensor.it_will_rain
    to: 'on'
  condition:
    condition: and
    conditions:
      - condition: state
        entity_id: group.family
        state: 'home'
      - condition: time
        after: '7:00:00'
        before: '23:59:59'
  action:
    - service: light.turn_on
      data:
        entity_id: light.gatewa_ambient_light
        rgb_color: [0,190,255]
        brightness: 45
```

### Samsung Multiroom

This custom component is used for controlling volume, and source of my multiroom device like [Samsung Soundbar K650](https://www.samsung.com/us/televisions-home-theater/home-theater/sound-bars/samsung-hw-k650-soundbar-w-wireless-subwoofer-hw-k650-za/). It is based on [unofficial api](https://github.com/bacl/WAM_API_DOC/blob/master/API_Methods.md). This component is based on my older code [from this repository](https://github.com/macbury/ha_samsung_multi_room/)

``` yaml
media_player:
  - platform: samsung_multi_room
    name: "Soundbar" # name, otherwise it will use name of your soundbar
    host: 192.168.1.227 # ip of your soundbar
    max_volume: 20 # on this level glass breaks, and there are 80 levels more on K650...
```

### KKM

This component fetch information about my train card from [www.mpk.krakow.pl](http://www.mpk.krakow.pl) and creates sensor with information about how many days is left before expiration and on what tram lines it can be used for.

``` yaml
- platform: kkm
  name: Tram card
  identity: 12345678
  city_card: 12345678
```

### PublicTransit

Public transit uses data collected by [busix](https://github.com/macbury/busix) software that scraps Cracow public transit webpage and extracts departures of buses and trains. You can specify in component starting line stop and target line stop and system will refresh and calculate next departure. There is also custom lovelace component for displaying data. 

``` yaml
- platform: public_transit
  name: work
  from: "Białucha"
  to: "Wzgórza Krzesławickie"
  endpoint: "http://busix:5000/api"
```

### Lunching

Used for fetching information from [lunching.pl](http://lunching.pl) about what did I order to eat in work. Sensor contains information when food will be delivered and what was ordered.

``` yaml
- platform: lunching
  name: foooooooood
  username: macbury
  password: secret password here
```

### Cracow Air Quality

Simple integration with Air Quality stations in Cracow for getting "fresh" information. Data is fetched from [Cracow Air Quality Monitoring Page](http://monitoring.krakow.pios.gov.pl/)

``` yaml
- platform: cracow_air_quality
  station_id: 7
  name: 'nowa_huta'
```

### Harvest

Integration with [harvest](https://www.getharvest.com/) time tracking software. Mainly used for sending notification that work is done, and I should take my ass back to home.

``` yaml
- platform: harvest
  name: work
  account_id: 1234
  token: morphing-power-token
```

### Spotify Cover Sensor

This platform extracts colors from currently played song cover. If proper scene is activated, these colors are used for setting light color:

``` yaml
- platform: spotify_cover_sensor
  cache_path: '/config/spotify-token-cache.json'
```

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/8wh9JsnNPxU" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Third party components

Here are components written by other people that are not in HomeAssistant core.

### Alexa Media Player

[This component](https://github.com/keatontaylor/alexa_media_player) exposes all my alexa devices as media player. I can also use built in annoucment feature and send audio notifications.

### Google Geocode

The `google_geocode` sensor converts device tracker location into a human-readable address. Mainly used for checking in what city currently each device is.
