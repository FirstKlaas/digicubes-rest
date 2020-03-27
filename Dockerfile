FROM python:slim

WORKDIR /digicubes

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

RUN mkdir cfg
RUN mkdir logs

COPY ./cfg/development.yaml cfg/production.yaml
COPY requirements.txt .

RUN pip install --no-cache-dir wheel
RUN pip install --no-cache-dir digicubes-server

COPY rundigicubes.py .

ENV DIGICUBES_ENVIRONMENT=production
ENV DIGICUBES_CONFIG_PATH=cfg

VOLUME [ "/cfg"]