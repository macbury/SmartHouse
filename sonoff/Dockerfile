FROM amd64/node:10.16.0-jessie

RUN git clone https://github.com/mdopp/simple-sonoff-server.git /server
WORKDIR /server

RUN npm install
ADD sonoff.config.json .
CMD node sonoff.server.js