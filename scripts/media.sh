#!/usr/bin/env bash
SUBCOMMAND=${1}
declare -a MEDIA_SHARES=("UsbDisk" "Movies" "MoviesAndTV" "Music" "Books" "SDDisk1")

function media_command_mount() {
  for share in "${MEDIA_SHARES[@]}"
  do
    mount_share $share
  done
}

function media_command_unmount() {
  for share in "${MEDIA_SHARES[@]}"
  do
    unmount_share $share
  done
}

function media_command_up() {
  docker-compose --file docker-compose.media.yaml --project-name media up
}

function media_command_down() {
  docker-compose --file docker-compose.media.yaml --project-name media down --remove-orphans
}

function media_command_logs() {
  docker-compose --file docker-compose.media.yaml --project-name media logs -f
}

function media_command_start() {
  sudo systemctl start media;
}

function media_command_stop() {
  sudo systemctl stop media;
}

function media_command_restart() {
  sudo systemctl restart media;
}

function media_command_help() {
  echo "
  🏡  SmartHouse Media

  $ smart-house media help                                  - print this help message
  $ smart-house media start                                 - start all media stuff
  $ smart-house media stop                                  - stop all media stuff
  $ smart-house media restart                               - restart all media stuff
  $ smart-house media mount                                 - mount media shares
  $ smart-house media unmount                               - unmount media shares
  "
}

function media_validate_command() {
  if [ "$(type -t media_command_${SUBCOMMAND})" = function ]; then
    return 0
  elif [ -z "$SUBCOMMAND" ]; then
    media_command_help;
    return 1
  else
    echo "Unknown media command: ${SUBCOMMAND}";
    return 1
  fi
}

function media_execute_command() {
  if ! media_validate_command; then
    return 1
  fi
  media_command_${SUBCOMMAND} ${COMMAND_ARGS}
  return $?
}

if ! media_execute_command; then
  return 1
fi
