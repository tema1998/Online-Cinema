FROM python:3.10.7-slim-buster

RUN apt-get update && \
  apt-get install --no-install-recommends -y python-psycopg2 wget make wait-for-it\
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/app
COPY /.env ./

COPY /content_service/src/start.sh ./
COPY /content_service/src/poetry.lock /content_service/src/pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY ./content_service/ /srv/app

EXPOSE 8000

CMD ["/bin/bash", "start.sh"]
