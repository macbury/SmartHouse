FROM alpine:3.13

WORKDIR /app

RUN apk add --no-cache \
      nodejs

# Build tools required to install serialport, a zwave-js dependency
RUN apk add --no-cache \
      g++ \
      git \
      linux-headers \
      make \
      npm \
      python3

RUN npm install npm@latest -g

WORKDIR /app

ARG ZWAVE_JS_PACKAGE=zwave-js@8.11.6
ARG ZWAVE_JS_SERVER_PACKAGE=@zwave-js/server@1.15.0
ARG NPM_INSTALL_FLAGS=

RUN npm install ${NPM_INSTALL_FLAGS} ${ZWAVE_JS_SERVER_PACKAGE} ${ZWAVE_JS_PACKAGE}

RUN apk add --no-cache \
      jq

WORKDIR /app

ENV NODE_ENV=production

COPY docker-entrypoint.sh /usr/local/bin/
COPY options.js .
RUN mkdir -p /cache/config /cache/db /logs

VOLUME "/cache"
EXPOSE 3000

ENV PATH=/app/node_modules/.bin:$PATH

ENV USB_PATH=/dev/zwave
ENV LOGFILENAME=/logs/zwave_%DATE%.log
# Path to persistent device configuration DB
ENV ZWAVEJS_EXTERNAL_CONFIG=/cache/db

RUN ls
ENTRYPOINT ["docker-entrypoint.sh"]
