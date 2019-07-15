## Provisioning all instances

Clone this repository on your local machine. Install [ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) and run the provision command:

```bash
# copy configuration for our inventory, Specify ip of all prepared servers
cp provision/inventory.ini.example provision/inventory.ini
# Just run the provision shit
bin/smart-house-provision server
```

## Configuring main HomeAssistant instance
Before starting smart house instance, there is a few things to do. Go to `/smart-house` directory and edit all `.env` files:

```bash
ssh <ssh-user>@<target-ip>
cd /smart-house

# Edit configuration under .env files
nano .env.crontab
nano .env.grafana
nano .env.influxdb
nano .env.pihole
nano .env.postgresql
nano .env.nextcloud
nano .env.plex
nano .env.home-assistant

# Generate mosquitto user and password
smart-house add-mosquitto-user home-assistant
# Add it to our .env.home-assitant
nano .env.home-assistant

# Configure your zones
cp home-assistant/components/zones.yaml.example home-assistant/components/zones.yaml
nano home-assistant/components/zones.yaml

# Start home assistant instance
smart-house start

# set key overwritewebroot to match your domain: (https://docs.nextcloud.com/server/13/admin_manual/configuration_server/reverse_proxy_configuration.html#overwrite-parameters)
nano /smart-house/.docker/data/nextcloud/config/config.php

# Generate long living token using home assistant panel
nano appdaemon/appdaemon.yaml # paste code here
smart-house restart

# Configure know devices
nano home-assistant/known_devices.yaml
smart-house restart
```