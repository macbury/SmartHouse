FROM mozilla/syncserver:latest

USER root
RUN apk --no-cache update && apk add --no-cache postgresql-libs && apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev 
RUN pip install psycopg2
USER app