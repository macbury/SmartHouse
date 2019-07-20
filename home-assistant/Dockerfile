FROM homeassistant/home-assistant:0.96.1

ENV TZ 'Europe/Warsaw'
RUN echo $TZ > /etc/timezone && \
      apt-get update && apt-get install -y tzdata && \
      rm /etc/localtime && \
      ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
      dpkg-reconfigure -f noninteractive tzdata && \
      apt-get clean

RUN pip3 install tensorflow
RUN apt-get update && apt-get install ffmpeg libatlas-base-dev libopenjp2-7 libtiff5 -y git curl zip

WORKDIR /tmp
RUN git clone --depth 1 https://github.com/tensorflow/models.git tensorflow-models
RUN curl -OL https://github.com/google/protobuf/releases/download/v3.4.0/protoc-3.4.0-linux-x86_64.zip
RUN unzip -a protoc-3.4.0-linux-x86_64.zip -d protobuf
RUN mv protobuf/bin /tmp/tensorflow-models/research

WORKDIR /tmp/tensorflow-models/research/

RUN ./bin/protoc object_detection/protos/*.proto --python_out=.
RUN mkdir -p /tensorflow/object_detection
RUN touch /tensorflow/object_detection/__init__.py
RUN mv object_detection/data /tensorflow/object_detection
RUN mv object_detection/utils /tensorflow/object_detection
RUN mv object_detection/protos /tensorflow/object_detection

WORKDIR /tmp
RUN wget http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_v2_coco_2018_01_28.tar.gz
RUN tar xvfz faster_rcnn_inception_v2_coco_2018_01_28.tar.gz
RUN cp /tmp/faster_rcnn_inception_v2_coco_2018_01_28/frozen_inference_graph.pb /tensorflow
RUN rm -rf /tmp/*

RUN apt-get update && apt-get install -y libxml2-dev libxslt1-dev zlib1g-dev

HEALTHCHECK --interval=60s --timeout=30s --start-period=300s --retries=3 CMD curl -f http://localhost:8123/ || exit 1

WORKDIR /usr/src/app

ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

ADD ./docker-entrypoint.sh /
CMD ["/docker-entrypoint.sh"]
