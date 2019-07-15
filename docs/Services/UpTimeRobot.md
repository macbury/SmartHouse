I really wanted to get notifications in case of downtime. Currently there is cool of service called [UptimeRobot](https://uptimerobot.com/) in which you can specify url to check. In case of downtime, UptimeRobot sents alerts. And there are also cool badges:

![Uptime Status](https://img.shields.io/uptimerobot/status/m782818639-f9a1f36b2acd090bbfaa4435.svg)
![Uptime last 7 days](https://img.shields.io/uptimerobot/ratio/7/m782818639-f9a1f36b2acd090bbfaa4435.svg)

The most important piece of software to check is of course HomeAssistant instance. The only thing exposed is `ping.txt` file inside `home-assitant/www/ping.txt`:

```nginx
  location /ping.txt {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_pass http://hass/local/ping.txt;
  }
```

If for some reason HomeAssistant container is down or the whole server just gone bananas, this file will not be served and response should `503 Bad Gateway`.