#!/bin/sh
set -e

if [ -z "$1" ]; then
  if [ ! -c "$USB_PATH" ]; then
    echo "USB path \"$USB_PATH\" does not exist or is not a character device"
    exit 1
  fi

  if [ -n "$NETWORK_KEY" ]; then
    echo "NETWORK_KEY is deprecated, use S0_LEGACY_KEY instead"
  fi

  set -- zwave-server --config options.js "$USB_PATH"
  echo "Starting zwave-server:" "$@"
elif [ "$1" = "server" ]; then
  shift
  set -- zwave-server "$@"
elif [ "$1" = "client" ]; then
  shift
  set -- zwave-client "$@"
fi

exec "$@"
