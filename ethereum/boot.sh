#!/bin/sh

echo "Booting..."

mkdir -p /root/.ethereum/

geth --datadir /data \
  --networkid $NETWORK_ID \
  --rpc \
  --rpcvhosts=*\
  --rpccorsdomain="*" \
  --ipcpath=/root/.ethereum/geth.ipc \
  --allow-insecure-unlock \
  --unlock $MAIN_ACCOUNT \
  --mine \
  --nodiscover \
  --graphql \
  --password /settings/password.txt
