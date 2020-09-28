# BUILDER stage
#
# pull official base image
FROM python:3.8-alpine as builder
LABEL stage=builder

# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONOTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install Pillow dependencies
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add jpeg-dev zlib-dev libjpeg \
    && pip install Pillow \
    && apk del build-deps

# install psycopg2 dependencies

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY . /usr/src/app/

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# FINAL stage
#
# pull official base image
FROM python:3.8-alpine

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media
WORKDIR $APP_HOME

# install dependencies
RUN apk update && apk add libpq sudo jpeg-dev zlib-dev libjpeg
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt . 
RUN chown -R app:app $APP_HOME
RUN chown -R app:app $HOME
RUN sudo -H pip install --upgrade pip
RUN sudo -H pip install --no-cache /wheels/*

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change user and run
USER app
RUN ./manage.py collectstatic --no-input
CMD gunicorn yatube.wsgi:application --bind 0:8000