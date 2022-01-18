FROM python:3.8
LABEL maintainer="info@affresco.io"


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PROJECT_ROOT /app
WORKDIR $PROJECT_ROOT

# Non scientific
RUN apt-get update && apt install -y python3-dev build-essential libpq-dev libmemcached-dev

# Scientific
# RUN apt-get update && apt install -y python3-dev build-essential libpq-dev libmemcached-dev zlib1g-dev libblas-dev liblapack-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


COPY . .

# EXPOSE 8000
# CMD ["python", "./manage.py", "runserver", "0.0.0.0:8000"]
