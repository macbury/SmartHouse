The whole infrastructure is controlled using my custom `smart-house` bash [shell script](https://github.com/macbury/SmartHouse/blob/master/bin/smart-house).

```bash
$ smart-house help

  🏡   SmartHouse

  $ smart-house help                                  - print this help message
  $ smart-house restart                               - restart all services
  $ smart-house docs                                  - start preview mkdocs process
  $ smart-house quick-restart                         - restart only home-assistant
  $ smart-house cleanup                               - cleanup docker shit
  $ smart-house ps                                    - show processes
  $ smart-house kiosk                                 - start kiosk dev mode
  $ smart-house unban <ip>                            - unban ip
  $ smart-house psql                                  - connect to docker postgresql instance
  $ smart-house migrate                               - migrate database
  $ smart-house health-check                          - ensure if home assistant is healthy
  $ smart-house mount-nas                             - mount nas shares
  $ smart-house start                                 - start all services
  $ smart-house status                                - status of all services
  $ smart-house logs                                  - print all logs
  $ smart-house stop                                  - stop all services
  $ smart-house ddns                                  - update dns on cloudflare
  $ smart-house backup                                - backup all data
  $ smart-house env                                   - print all envs
  $ smart-house dev                                   - dev mode
  $ smart-house lovelace                              - generate lovelace config
  $ smart-house lovelace-dev                          - regenerate lovelace on file change
  $ smart-house validate-config                       - check if config is ok
  $ smart-house build container                       - rebuild container
  $ smart-house upgrade                               - upgrade current home assistant
  $ smart-house docker-compose args                   - run docker compose commands
  $ smart-house add-mosquitto-user name               - creates new user and generates for him random password
  $ smart-house disable-aotec-blinking                - disable stupid blinking on aotec dongle

```