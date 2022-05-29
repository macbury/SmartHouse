docker exec -u 33 -it support_nextcloud_1 bash
./occ maintenance:mode --on
./occ upgrade
./occ maintenance:mode --off
