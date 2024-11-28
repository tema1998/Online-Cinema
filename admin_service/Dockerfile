FROM python:3.10.8

SHELL ["/bin/bash", "-c"]


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY /.env ./
COPY /admin_service/requirements.txt requirements.txt

RUN pip install --upgrade pip \
  && pip install -r requirements.txt --no-cache-dir

COPY ./admin_service/ .

RUN  python3 manage.py collectstatic --noinput

EXPOSE 8000

CMD  ["gunicorn","-b","0.0.0.0:8000","config.wsgi:application"]
