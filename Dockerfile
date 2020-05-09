FROM continuumio/miniconda3:4.8.2

RUN mkdir -p /app
COPY . /app
WORKDIR /app

RUN /bin/bash -l -c 'source setup/setup.sh'
