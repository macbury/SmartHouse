#!/usr/bin/env bash
SUBCOMMAND=${1}
shift 1
SUBCOMMAND_ARGS=${@}

function support_command_up() {
  docker-compose --file docker-compose.support.yaml --project-name support up
}

function support_command_down() {
  docker-compose --file docker-compose.support.yaml --project-name support down
}

function support_command_logs() {
  docker-compose --file docker-compose.support.yaml --project-name support logs -f
}

function support_command_start() {
  sudo systemctl start support;
}

function support_command_stop() {
  sudo systemctl stop support;
}

function support_command_restart() {
  sudo systemctl restart support;
}

function support_command_docker-compose() {
  eval "docker-compose --file docker-compose.support.yaml --project-name support ${SUBCOMMAND_ARGS}"
}

function support_command_help() {
  echo "
  🏡  SmartHouse support

  $ smart-house support help                                  - print this help message
  $ smart-house support start                                 - start all support stuff
  $ smart-house support stop                                  - stop all support stuff
  $ smart-house support restart                               - restart all support stuff
  "
}

function support_validate_command() {
  if [ "$(type -t support_command_${SUBCOMMAND})" = function ]; then
    return 0
  elif [ -z "$SUBCOMMAND" ]; then
    support_command_help;
    return 1
  else
    echo "Unknown media command: ${SUBCOMMAND}";
    return 1
  fi
}

function support_execute_command() {
  if ! support_validate_command; then
    return 1
  fi
  support_command_${SUBCOMMAND} ${COMMAND_ARGS}
  return $?
}

if ! support_execute_command; then
  return 1
fi