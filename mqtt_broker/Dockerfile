FROM ubuntu:20.04

LABEL ece449=true
# backend system dependencies
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Moscow
RUN apt-get install -y tzdata

RUN apt-get update && apt-get install -y python3-opencv

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

# install backend packages
RUN pip3 install -r requirements.txt
COPY . /app
RUN echo $(ls)

# host mqtt
RUN useradd -ms /bin/bash test
# USER test
CMD ./start.sh
