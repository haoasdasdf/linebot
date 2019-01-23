FROM python:3.7.1

ENV APP_PATH /usr/src/app

RUN mkdir -p $APP_PATH
WORKDIR $APP_PATH/api

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
