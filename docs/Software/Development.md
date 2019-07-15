Most of services used by my Smart House resides inside [docker](https://www.docker.com/) containers. Thanks to that I can get about 90% similar setup on my dev machine.

Configuring of the dev environment starts from copying all `.env.example` files and filling them with credentials and configurations:

```bash
cp .env.crontab.example .env.crontab
cp .env.grafana.example .env.grafana
cp .env.influxdb.example .env.influxdb
cp .env.pihole.example .env.pihole
cp .env.postgresql.example .env.postgresql
cp .env.nextcloud.example .env.nextcloud
cp .env.plex.example .env.plex
cp .env.home-assistant.example .env.home-assistant
```

Next there are few files used by docker that needs to be created(docker would create a folder for that not a file)

```bash
mkdir -p .docker/data/mosquitto
mkdir -p .docker/log

touch .docker/data/mosquitto/users.db
touch .docker/log/fail2ban.log
touch .docker/log/mosquitto.log
```

And finally some python dependencies:
```bash
sudo pip3 install -r requirements.txt
```

Now we can Rock & Roll. There are two dev commands, the first one is `dev` that bootups all containers:
```bash
SMART_HOUSE_DIR=$(pwd) bin/smart-house dev
```

And here is simple command that watches directory with lovelace configuration, and regenerates all configuration on change:
```bash
SMART_HOUSE_DIR=$(pwd) bin/smart-house lovelace-dev
```