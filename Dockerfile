FROM python:slim

WORKDIR /digicubes

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

RUN mkdir cfg
RUN mkdir logs

COPY cfg .
COPY requirements.txt .

RUN pip install --no-cache-dir wheel
RUN pip uninstall digicubes-server
RUN pip install --no-cache-dir digicubes-server

ENV DIGICUBES_CONFIG_FILE=configuration.yaml
ENV DIGICUBES_CONFIG_PATH=cfg

RUN digicubes-server setup

CMD ["digicubes-server", "run"]