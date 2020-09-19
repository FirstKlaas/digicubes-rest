FROM python:slim

LABEL maintainer="klaas.nebuhr@gmail.com"

WORKDIR /digicubes

RUN apt-get update \
&& apt-get install apt-utils -y \
&& apt-get install gcc -y \
&& apt-get install -y --no-install-recommends git \
&& apt-get clean

RUN mkdir -p data
RUN mkdir -p logs
RUN mkdir -p digicubes_rest

RUN pip install --no-cache-dir wheel
RUN pip install --upgrade pip

COPY requirements.txt .
COPY rundigicubes.py .
COPY digicubes_rest/ digicubes_rest/
RUN pip install -r requirements.txt


EXPOSE 3548/tcp

ENV DIGICUBES_DATABASE_URL sqlite://data/digicubes.db
ENV DIGICUBES_SECRET b3j6casjk7d8szeuwz00hdhuw4ohwDu9o

VOLUME /digicubes/data
VOLUME /digicubes/logs

CMD ["python", "rundigicubes.py"]

# Last change 19.09.2020 - 8:44
