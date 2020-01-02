#!/bin/bash

VACUUM_SERVER=192.168.1.12
VACUUM_PORT=10005

SLAM_LOG=/var/run/shm/SLAM_fprintf.log
MAP_FILES=$(find /var/run/shm/ -iname '*.ppm')
set -- $MAP_FILES
MAP_FILE=$1

if [ ! -f $SLAM_LOG ]; then
    echo "$SLAM_LOG missing..."
    exit 0
fi
if [ -z "$MAP_FILE" ] || [ ! -f $MAP_FILE ]; then
    echo "Map file missing..."
    exit 0
fi

cp $MAP_FILE /tmp/mapfile
cp $SLAM_LOG /tmp/slamlog

echo SLAM_LOG=$SLAM_LOG
echo MAP_FILE=$MAP_FILE

# Send stuff to endpoint
printf "Sending... $MAP_FILE and $SLAM_LOG"
curl --write-out '%{http_code}' --silent --output /dev/null -X POST -F map=@/tmp/mapfile -F log=@/tmp/slamlog http://$VACUUM_SERVER:$VACUUM_PORT/map