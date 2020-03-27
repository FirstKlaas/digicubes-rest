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
RUN pip install --no-cache-dir digicubes-server

COPY rundigicubes.py .

ENV DIGICUBES_CONFIG_FILE=configuration.yaml
ENV DIGICUBES_CONFIG_PATH=cfg

VOLUME [ "/cfg"]

CMD ["python", "rundigicubes.py"]