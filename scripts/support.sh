#!/usr/bin/env bash
SUBCOMMAND=${1}
shift 1
SUBCOMMAND_ARGS=${@}

function support_command_up() {
  docker-compose --file docker-compose.support.yaml --project-name support up
}

function support_command_fix() {
  /usr/local/bin/docker-compose --file docker-compose.support.yaml --project-name support restart influxdb;
  /usr/local/bin/docker-compose --file docker-compose.support.yaml --project-name support restart rss-bridge;
}

function support_command_down() {
  docker-compose --file docker-compose.support.yaml --project-name support down
}

function support_command_docker-compose() {
  docker-compose --file docker-compose.support.yaml --project-name support $SUBCOMMAND_ARGS
}

function support_command_logs() {
  docker-compose --file docker-compose.support.yaml --project-name support logs --tail=100 -f
}

function support_command_mysql() {
  docker-compose --file docker-compose.support.yaml --project-name support run --rm mysql bash -l -c "mysql -h mysql -u root --password=$MYSQL_ROOT_PASSWORD"
}

function support_command_start() {
  sudo systemctl start support;
}

function support_command_stop() {
  sudo systemctl stop support;
}

function support_command_restart() {
  support_command_stop;
  support_command_start;
}

function support_command_health-check() {
  docker ps | grep support | grep unhealthy;
  local status=$?;
  if [ $status -eq 0 ]; then
    echo "Unhealthy containers, fire in the hole!";
    support_command_restart;
  fi
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
  $ smart-house support docker-compose                        - manage docker compose
  $ smart-house support mysql                                 - connect to mysql
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
