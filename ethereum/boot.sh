#!/bin/sh

echo "Booting..."

mkdir -p /root/.ethereum/

geth --datadir /data \
  --metrics.influxdb \
  --metrics.influxdb.endpoint=http://0.0.0.0:18086 \
  --metrics.influxdb.database=ethereum \
  --metrics.influxdb.username=$INFLUXDB_ADMIN_USER \
  --metrics.influxdb.password=$INFLUXDB_ADMIN_PASSWORD \
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