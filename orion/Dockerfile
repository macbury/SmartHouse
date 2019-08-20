FROM ubuntu:18.04

EXPOSE 5000

RUN apt-get update && apt-get install \
  -y --no-install-recommends curl libmysqlclient-dev python-dev python python-setuptools python-pip build-essential git ca-certificates


RUN pip install setuptools --upgrade
RUN git clone https://github.com/LINKIWI/orion-server.git /server

WORKDIR /server

RUN pip install -r requirements.txt
RUN mkdir -p /etc/orion
ADD config.json /etc/orion/config.json

ENV PYTHONPATH /server
ADD entrypoint.sh .
ADD web/index.html .
ADD web/main.js .
RUN chmod +x ./entrypoint.sh
CMD ["bash", "entrypoint.sh"]