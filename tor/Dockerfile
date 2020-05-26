FROM alpine:latest

RUN apk update \
 && apk upgrade \
 && apk add tor \
 && rm /var/cache/apk/*

EXPOSE 9051
ADD ./torrc /etc/tor/torrc

RUN mkdir /data
USER tor
USER root
RUN chown tor /data
USER tor
CMD /usr/bin/tor -f /etc/tor/torrc