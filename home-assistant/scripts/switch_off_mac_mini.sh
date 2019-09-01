#!/usr/bin/env bash

ssh-keyscan -H 192.168.1.91 >> ~/.ssh/known_hosts
ssh -i /config/.storage/id_rsa macbury@192.168.1.91 'pmset sleepnow'