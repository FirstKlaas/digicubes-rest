FROM python:slim

LABEL maintainer="klaas.nebuhr@gmail.com"

WORKDIR /digicubes

RUN apt-get update \
&& apt-get install apt-utils -y \
&& apt-get install gcc -y \
&& apt-get install -y --no-install-recommends git \
&& apt-get clean

RUN mkdir -p data

RUN pip install --no-cache-dir wheel
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade --force-reinstall digicubes-server
RUN pip install --no-cache-dir --upgrade --force-reinstall git+https://github.com/FirstKlaas/digicubes-rest#egg=digicubes-server

EXPOSE 3000/tcp

ENV DIGICUBES_DATABASE_URL sqlite://data/digicubes.db
ENV DIGICUBES_SECRET b3j6casjk7d8szeuwz00hdhuw4ohwDu9o

VOLUME /digicubes/data

CMD ["digicubes-server", "run"]
