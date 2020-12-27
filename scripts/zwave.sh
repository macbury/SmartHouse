#!/usr/bin/env bash
SUBCOMMAND=${1}
shift 1
SUBCOMMAND_ARGS=${@}

function zwave_command_up() {
  docker-compose --file docker-compose.zwave.yaml --project-name zwave up
}

function zwave_command_down() {
  docker-compose --file docker-compose.zwave.yaml --project-name zwave down
}

function zwave_command_docker-compose() {
  docker-compose --file docker-compose.zwave.yaml --project-name zwave $SUBCOMMAND_ARGS
}

function zwave_command_logs() {
  docker-compose --file docker-compose.zwave.yaml --project-name zwave logs --tail=100 -f
}

function zwave_command_start() {
  sudo systemctl start zwave;
}

function zwave_command_stop() {
  sudo systemctl stop zwave;
}

function zwave_command_restart() {
  zwave_command_stop;
  zwave_command_start;
}

function zwave_command_docker-compose() {
  eval "docker-compose --file docker-compose.zwave.yaml --project-name zwave ${SUBCOMMAND_ARGS}"
}

function zwave_command_help() {
  echo "
  🏡  SmartHouse zwave

  $ smart-house zwave help                                  - print this help message
  $ smart-house zwave start                                 - start all zwave stuff
  $ smart-house zwave stop                                  - stop all zwave stuff
  $ smart-house zwave restart                               - restart all zwave stuff
  $ smart-house zwave docker-compose                        - manage docker compose
  $ smart-house zwave mysql                                 - connect to mysql
  "
}

function zwave_validate_command() {
  if [ "$(type -t zwave_command_${SUBCOMMAND})" = function ]; then
    return 0
  elif [ -z "$SUBCOMMAND" ]; then
    zwave_command_help;
    return 1
  else
    echo "Unknown media command: ${SUBCOMMAND}";
    return 1
  fi
}

function zwave_execute_command() {
  if ! zwave_validate_command; then
    return 1
  fi
  zwave_command_${SUBCOMMAND} ${COMMAND_ARGS}
  return $?
}

if ! zwave_execute_command; then
  return 1
fi
