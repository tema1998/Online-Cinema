FROM python:3.10-slim-buster

WORKDIR /tests

COPY poetry.lock pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY tests/start.sh ./
COPY tests/. .
COPY src/. /src/.

ENV PYTHONPATH "${PYTHONPATH}:/"

CMD ["/bin/bash", "start.sh"]
