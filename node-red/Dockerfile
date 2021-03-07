FROM nodered/node-red:latest-12

USER root

RUN apk update && apk add py3-setuptools ffmpeg
RUN curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
RUN chmod a+rx /usr/local/bin/youtube-dl
RUN youtube-dl --version
USER node-red

