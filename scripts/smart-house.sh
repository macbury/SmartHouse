#!/usr/bin/env bash
function smart_house_load_variables() {
  if [ ! -f ${SMART_HOUSE_DIR}/$1 ]; then
    echo "File ${SMART_HOUSE_DIR}/$1 do not exists!"
    exit 1;
  fi;

  export $(cat "${SMART_HOUSE_DIR}/$1";)
}

function smart_house_validate_command() {
  if [ "$(type -t smart_house_command_${COMMAND})" = function ]; then
    return 0
  elif [ -z "$COMMAND" ]; then
    smart_house_command_help;
    return 1
  else
    echo "Unknown command: ${COMMAND}";
    return 1
  fi
}

function smart_house_command_restart() {
  smart_house_command_stop;
  smart_house_command_start;
}

function smart_house_command_quick-restart() {
  docker-compose restart home-assistant
}

function smart_house_command_cleanup() {
  docker rmi $(docker images -q -f dangling=true)
  ​docker volume rm $(docker volume ls -qf dangling=true)
}

function smart_house_command_bash() {
  docker-compose run --rm home-assistant bash
}

function smart_house_command_ipfs() {
  docker-compose exec ipfs ipfs $COMMAND_ARGS
}

function smart_house_command_env() {
  env
}

function smart_house_command_ps() {
  docker-compose ps
}

function unmount_share() {
  declare share=$1
  sudo umount /mnt/$share
}

function mount_share() {
  declare share=$1
  echo "Mounting $share"
  sudo mkdir -p /mnt/$share
  unmount_share $share
  echo $HOME_ASSISTANT_QNAP_PASSWORD | sudo sshfs -o allow_other,password_stdin $HOME_ASSISTANT_QNAP_USERNAME@192.168.1.181:/share/$share/ /mnt/$share
}

function smart_house_command_backup() {
  BACKUP_STORAGE=/mnt/homes/SmartHouse;
  TIMESTAMP=$(date +%Y/%m/%d_%H:%M:%S);
  BACKUP_FOLDER="$SMART_HOUSE_DIR/.backups/";
  BACKUP_FILE="${BACKUP_FOLDER}smart-house_$(date +"%Y%m%d_%H%M%S").zip";
  mkdir -p $BACKUP_FOLDER;
  systemctl stop smart-house;
  systemctl stop support;
  systemctl stop media;
  echo $BACKUP_FILE
  zip -1 -r $BACKUP_FILE $SMART_HOUSE_DIR -x"smart-house/tmp" -x"*.log" -x"*.backups" -x"smart-house/.docker/data/plex/config/Library/Application Support/Plex Media Server/Cache/**/*" -x"smart-house/.docker/data/plex/config/Library/Application Support/Plex Media Server/Media/**/*" -x"*.AppleDouble" -x"smart-house/.docker/data/dpodcast";
  systemctl start support;
  systemctl start smart-house;
  mkdir -p $BACKUP_STORAGE;
  cp $BACKUP_FILE $BACKUP_STORAGE;
  echo $TIMESTAMP > .backups/performed_at.txt
  rm $BACKUP_FILE;
  find $BACKUP_STORAGE -mtime +3 -type f -delete;
}

function smart_house_command_build() {
  sudo docker-compose build $COMMAND_ARGS;
}

function smart_house_command_upgrade() {
  sudo docker-compose build home-assistant;
  sudo docker image prune -f
  sudo docker volume prune -f
}

function smart_house_command_add-mosquitto-user() {
  random_password=$(openssl rand -base64 32 | rev | cut -b 2- | rev);
  mkdir -p $SMART_HOUSE_DIR/.docker/data/mosquitto;
  mosquitto_passwd -b $SMART_HOUSE_DIR/.docker/data/mosquitto/users.db $COMMAND_ARGS $random_password;

  docker-compose restart mqtt;

  echo "Username: $COMMAND_ARGS";
  echo "Password: $random_password";
}

function smart_house_command_docs() {
  export LC_ALL=C.UTF-8
  export LANG=C.UTF-8
  mkdocs serve --livereload --dev-addr 0.0.0.0:7000
}

function smart_house_command_ddns() {
  bin/ddns.py $MAIN_DOMAIN $HOME_ASSISTANT_SUBDOMAIN 1;
  bin/ddns.py $MAIN_DOMAIN budget.$HOME_ASSISTANT_SUBDOMAIN 1;
  bin/ddns.py $MAIN_DOMAIN notes.$HOME_ASSISTANT_SUBDOMAIN 0;
  bin/ddns.py $MAIN_DOMAIN $HOME_ASSISTANT_VPNDOMAIN 0;
}

function smart_house_command_certbot() {
  systemctl stop nginx;
  certbot renew --no-self-upgrade;
  systemctl start nginx;
}

function smart_house_command_logs() {
  eval "docker-compose logs --tail=1000 -f ${COMMAND_ARGS}"
}

function smart_house_command_docker-compose() {
  eval "docker-compose ${COMMAND_ARGS}"
}

function smart_home_command_disable-aotec-blinking() {
  echo -e '\x01\x08\x00\xF2\x51\x01\x00\x05\x01\x51' | cu -l $HOME_ASSISTANT_ZWAVE_DEV -s 115200
}

function smart_house_command_stop() {
  sudo systemctl stop smart-house;
}

function smart_house_command_dev() {
  export HOME_ASSISTANT_LOGGER=debug;
  smart_house_command_lovelace;
  docker-compose down;
  docker-compose kill;
  docker-compose up --remove-orphans;
}

function smart_house_command_psql() {
  PGPASSWORD=$POSTGRES_PASSWORD psql --host localhost --username=$POSTGRES_USER --port=4101 $POSTGRES_DB;
}

function smart_house_command_lovelace() {
  python3 $SMART_HOUSE_DIR/bin/lovelace-gen.py $SMART_HOUSE_DIR/home-assistant/lovelace
}

function smart_house_command_lovelace-dev() {
  smart_house_command_lovelace;
  echo "Watching lovelace directory for changes...";
  while true; do
    fswatch -r -1 $SMART_HOUSE_DIR/home-assistant/lovelace/ $SMART_HOUSE_DIR/home-assistant/www/ --include=.yaml
    smart_house_command_lovelace;
    echo "Regenerated config!";
    sleep 1;
  done
}

function smart_house_command_validate-config() {
  HOME_ASSISTANT_DB_URL=sqlite:///tmp/test hass -c home-assistant/ --script check_config --info all
}

function smart_house_command_health-check() {
  docker ps | grep smart-house | grep unhealthy;
  local status=$?;
  if [ $status -eq 0 ]; then
    echo "Unhealthy containers, fire in the hole!";
    smart_house_command_restart;
  fi
}

function smart_house_command_unban() {
  sudo fail2ban-client set ha unbanip ${COMMAND_ARGS};
  sudo fail2ban-client set nginx-noscript unbanip ${COMMAND_ARGS};
  sudo fail2ban-client set nginx-http-auth unbanip ${COMMAND_ARGS};
  sudo fail2ban-client set nginx-badbots unbanip ${COMMAND_ARGS};
  sudo fail2ban-client set nginx-forbidden unbanip ${COMMAND_ARGS};
  sudo fail2ban-client set mosquitto-auth unbanip ${COMMAND_ARGS};
}

function smart_house_command_start() {
  smart_house_command_lovelace;
  sudo systemctl start smart-house;
  sudo systemctl restart fail2ban;
}

function smart_house_command_status() {
  sudo systemctl status smart-house;
}

function smart_house_execute_command() {
  if ! smart_house_validate_command; then
    return 1
  fi
  smart_house_command_${COMMAND} ${COMMAND_ARGS}
  return $?
}

function smart_house_command_media() {
  source "${SMART_HOUSE_DIR}/scripts/media.sh"
}

function smart_house_command_pihole() {
  source "${SMART_HOUSE_DIR}/scripts/pihole.sh"
}

function smart_house_command_support() {
  source "${SMART_HOUSE_DIR}/scripts/support.sh"
}