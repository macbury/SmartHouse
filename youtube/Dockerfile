FROM archlinux/base

RUN pacman -Sy --noconfirm shards crystal imagemagick librsvg \
    which pkgconf gcc ttf-liberation && \
    git clone https://github.com/omarroth/invidious

WORKDIR /invidious

RUN shards && \
    crystal build src/invidious.cr

EXPOSE 3000

CMD [ "/invidious/invidious" ]