## My OpenSource Projects

### DPodcast
[DPodcast](https://github.com/macbury/DPodcast) converts youtube channels into mp3 and generates podcasts xml. I use this to have ability to listen to my favorite channels(that have mostly people talking to camera, why they don't share their content in podcast form ?!) on my phone in offline mode without paing for youtube red. All content is shared over [IPFS](https://ipfs.io)

### mqtt2wol
[mqtt2wol](https://github.com/macbury/mqtt2wol) gateway is used to send wol packets over mqtt. This is installed on separate Raspberry PI. HomeAssistant allows to [send wol packages](https://www.home-assistant.io/components/wake_on_lan/) but that would require to [add host flag](https://docs.docker.com/compose/compose-file/#network_mode) but that blows my docker setup up.

### mqtt2rf
[mqtt2rf](https://github.com/macbury/mqtt2rf) gateway is used to for relaying 433/315MHz LPD/SRD signals with generic low-cost GPIO RF modules on a Raspberry Pi.

### yt-music-download-helper
[yt-music-download-helper](https://github.com/macbury/yt-music-download-helper) is simple web ui that allows me to download video from YouTube, extract music from it and place it inside my QNAP Nas.

### Busix
[Busix](https://github.com/macbury/busix) is self hosted web scrapper that extract information from [Cracow public transit webpage](http://www.mpk.krakow.pl/pl/page-f3044045/) (that for some reason, still in 2019 uses table in table layout for displayin data.) All scrapped data is exposed through graphql endpoint:

```graphql
{
  departures(from: "Białucha", to: "Wzgórza Krzesławickie", at: "10 minutes from now"){
    edges {
      node {
        line {
          name
          kind
        }

        time {
          formatted
          distance
        }
      }
    }
  }
}
```

## Other OpenSource projects

### HomeAssistan
[Home Assistant](https://www.home-assistant.io/) my main home automation software. I decided to use it because all configuration can be done by simple YAML files that can be stored inside git repository and UI is pretty decent and touch friendly.

### Ansible
[Ansible](https://www.ansible.com/) is nice nifty tool that helps me provisioning all running computer in my house(vacuum, smart panel, raspberry pi etc.). All provisioning scripts resides [here](https://github.com/macbury/SmartHouse/tree/master/provision).

### Docker
[Docker](https://www.docker.com/) is for managing all containers with software used in my SmartHome. Before I did use [hassbian](https://www.home-assistant.io/docs/installation/hassbian/installation/) but that was a bit off hassle if on upgrade something did blow or HomeAssistant did break something, and rollback was required. [Hass.io](https://www.home-assistant.io/hassio/) hides to much from me so I decided to prepare my own solution.

### Ubuntu 18.04 LTS
[Ubuntu](https://www.ubuntu.com/) it is pretty good linux with pretty good support.

### Appdaemon
[Appdaemon](https://appdaemon.readthedocs.io/en/stable/) is pretty decent extension for HomeAssistant automations. At some level I needed to [put more logic to automations](/Software/AppDaemon) and YAML files become unreadable for puny human.

### PiHole
Everybody is tracking you, Google, Russia(damn you Putin), China(damn you commies) and others. [PiHole](https://pi-hole.net/) is nice software that blocks Ads/Trackin site on the DNS level. Additionaly I have mapped on my router Google DNS like 8.8.8.8 to point to PiHole instance.

### PostgreSQL
[PostgreSQL](https://www.postgresql.org/) is main database used by HomeAssistant, Nextcloud and Firefly iii. Alternative would be eating glass or MySQL.

### InfluxDB and Grafana
[Influxdb](https://www.influxdata.com/) is backend database optimized for time series data, that is collected from HomeAssistant. [Grafana](https://grafana.com/) is used as analitics dashboard for analyzing data in form of nice and sexy charts.

### UFW and Fail2ban
[UFW](https://help.ubuntu.com/community/UFW) is a firewall for sane people. Used to restrict access to smart home server. There is also a [Fail2ban](https://www.fail2ban.org/wiki/index.php/Main_Page). It looks on logs from nginx, HomeAssistant and other services, and if it detect some kind of funky activity, then blocks it using system firewall

### CloudFlare
[CloudFlare](https://www.cloudflare.com/) My smart home ip is hidden behind domain and cloudflare dns server. There is a cron job that checks my current phone ip and updates it on the cloudflare.

### Plex
Pretty nice media server. [Plex](https://www.plex.tv/) is running on HomeAssistant computer and consumes photos and videos QNAP NAS. It has native client for Android/LG Web OS/Playstation 4 etc.

### NextCloud
[NextCloud](https://nextcloud.com/) is mainly used for providing calendar with CalDav and nice ui. This calendar is used mainly for triggering automations on specific times(heating, cat feeding etc.) and I wanted to avoid Google Calendar.

### Slack
[Slack](https://slack.com/) is used for sending notifications. I have my own home workspace that is shared with my wife.

### IPFS
[IPFS](https://ipfs.io) stands for Interplanetary File System. At its core it is a versioned file system which can store files and track versions over time, very much like Git. It also defines how files move across a network, making it a distributed file system, much like BitTorrent. In combining these two properties, IPFS enables a new permanent web and augments the way we use existing internet protocols like HTTP.

### IFTT
[IFTT](https://ifttt.com/discover) is used for triggering stuff using webhooks that don't expose APIs

### Sonarr, Bazarr and Transmission
[Sonarr](https://sonarr.tv/) and [Transmission](https://transmissionbt.com/) is used for tracking TV shows and Music. If a new show appear it is automatically downloaded using transmission. After download is completed stuff is moved to my NAS and Plex reindex everything. [Bazarr](https://www.bazarr.media/) is then used for finding polish subtitles.

### ESPHome
[ESPHome](https://esphome.io/) is a system to control your ESP8266/ESP32 by simple yet powerful configuration files and control them remotely through Home Automation systems.

### Firefly III
[Firefly III](https://firefly-iii.org/) is budget managment software.
