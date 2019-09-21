# Notice:
# When updating this file, please also update virtualization/Docker/Dockerfile.dev
# This way, the development image and the production image are kept in sync.

FROM python:3.7-buster
LABEL maintainer="Paulus Schoutsen <Paulus@PaulusSchoutsen.nl>"

# Uncomment any of the following lines to disable the installation.
#ENV INSTALL_TELLSTICK no
#ENV INSTALL_OPENALPR no
#ENV INSTALL_FFMPEG no
#ENV INSTALL_LIBCEC no
#ENV INSTALL_SSOCR no
#ENV INSTALL_DLIB no
#ENV INSTALL_IPERF3 no
#ENV INSTALL_LOCALES no

ENV TZ 'Europe/Warsaw'
RUN echo $TZ > /etc/timezone && \
      apt-get update && apt-get install -y tzdata && \
      rm /etc/localtime && \
      ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
      dpkg-reconfigure -f noninteractive tzdata && \
      apt-get clean

RUN apt-get update && apt-get install ffmpeg libatlas-base-dev libopenjp2-7 libtiff5 -y git curl zip libxml2-dev libxslt1-dev zlib1g-dev \
                                     build-essential libxrandr-dev nmap net-tools libcurl3-dev bluetooth libglib2.0-dev libbluetooth-dev \
                                     libsodium23 libudev-dev libmpc-dev libmpfr-dev libgmp-dev ffmpeg iperf3 \
                                     libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev \
                                     cmake git swig && apt-get install -y --no-install-recommends locales && apt-get clean

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
RUN locale-gen

VOLUME /config

RUN git clone https://github.com/home-assistant/home-assistant.git /usr/src/app

WORKDIR /usr/src/app
ENV VERSION 0.99.2
RUN git fetch --all --tags --prune
RUN git checkout tags/$VERSION -b current

# Install hass component dependencies
RUN pip3 install --no-cache-dir -r requirements_all.txt && \
    pip3 install --no-cache-dir mysqlclient psycopg2 uvloop==0.12.2 cchardet cython tensorflow

EXPOSE 8123
EXPOSE 8300
EXPOSE 51827

HEALTHCHECK --interval=60s --timeout=60s --start-period=300s --retries=6 CMD curl -f http://localhost:8123/ || exit 1
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

ENTRYPOINT ["/tini", "--"]

ADD ./docker-entrypoint.sh /
CMD ["/docker-entrypoint.sh"]