FROM ubuntu:20.04

LABEL ece449=true
# backend system dependencies
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

# install backend packages
RUN pip3 install -r requirements.txt
COPY . /app

# host website
CMD flask run --host 0.0.0.0
