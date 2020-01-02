#!/usr/bin/env bash
SUBCOMMAND=${1}

function pihole_command_start() {
  sudo systemctl start pihole
}

function pihole_command_stop() {
  sudo systemctl stop pihole
}

function pihole_command_status() {
  sudo systemctl status pihole
}

function pihole_command_restart() {
  sudo systemctl restart pihole
}

function pihole_command_up() {
  docker run \
    --name adguardhome \
    -v "$SMART_HOUSE_DIR/.docker/data/adguard/work:/opt/adguardhome/work" \
    -v "$SMART_HOUSE_DIR/.docker/data/adguard/conf:/opt/adguardhome/conf" \
    --net=host \
    --rm \
    -p 53:53/tcp \
    -p 53:53/udp \
    -p 67:67/udp \
    -p 68:68/tcp \
    -p 68:68/udp \
    -p 6080:80/tcp \
    -p 6443:443/tcp \
    -p 853:853/tcp \
    -p 6300:3000/tcp \
    adguard/adguardhome
}

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