#!/usr/bin/env bash
SUBCOMMAND=${1}

function pihole_command_start() {
  sudo systemctl start pihole
}

function pihole_command_stop() {
  sudo systemctl stop pihole
}

function pihole_command_restart() {
  sudo systemctl restart pihole
}

function pihole_command_up() {
  docker run \
    --name pihole \
    --cap-add NET_ADMIN \
    -p 53:53/tcp \
    -p 53:53/udp \
    -p 4104:80 \
    -e TZ="Europe/Warsaw" \
    -e VIRTUAL_HOST="https://${HOME_ASSISTANT_DOMAIN}/pihole/" \
    -e PROXY_LOCATION="pihole" \
    -e VIRTUAL_PORT="443" \
    -e ServerIP="192.168.1.12" \
    --env-file="$SMART_HOUSE_DIR/.env.pihole" \
    --env-file="$SMART_HOUSE_DIR/.env.local" \
    -v "$SMART_HOUSE_DIR/.docker/data/pihole/pihole:/etc/pihole" \
    -v "$SMART_HOUSE_DIR/.docker/data/pihole/dnsmasq.d:/etc/dnsmasq.d/" \
    --dns=127.0.0.1 \
    --dns=1.1.1.1 \
    --restart=unless-stopped \
    pihole/pihole:latest
}
# https://github.com/pi-hole/docker-pi-hole/blob/master/docker_run.sh

function pihole_command_help() {
  echo "
  🏡  SmartHouse PiHole

  $ smart-house pihole help                                  - print this help message
  $ smart-house pihole up                                    - up pihole
  $ smart-house pihole start                                 - start pihole
  $ smart-house pihole stop                                  - stop pihole
  $ smart-house pihole restart                               - restart pihole
  "
}

function pihole_validate_command() {
  if [ "$(type -t pihole_command_${SUBCOMMAND})" = function ]; then
    return 0
  elif [ -z "$SUBCOMMAND" ]; then
    pihole_command_help;
    return 1
  else
    echo "Unknown media command: ${SUBCOMMAND}";
    return 1
  fi
}

function pihole_execute_command() {
  if ! pihole_validate_command; then
    return 1
  fi
  pihole_command_${SUBCOMMAND} ${COMMAND_ARGS}
  return $?
}

if ! pihole_execute_command; then
  return 1
fi