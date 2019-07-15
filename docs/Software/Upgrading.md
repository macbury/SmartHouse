Most of upgrades are done by downloading or building new docker container.

### Upgrading Home Assistant
Edit version of docker image in first line of Dockerfile inside `home-assistant` directory. Then run command:

```bash
smart-house upgrade
smart-house restart
```

If everything still works, commit changes and tag the release:

```bash
git commit -a -m "New upgrade"
git tag v0.93.2
git push origin master
git push origin v0.93.2
```

### Upgrading rest of stuff

Edit `docker-compose.yaml`, increase version for image. Because we have our dns server inside Docker container the best thing to do is to run pull first, and then restart all containers:

```bash
smart-house docker-compose pull name-of-upgraded-service
smart-house restart
```