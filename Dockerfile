FROM python:slim

LABEL maintainer="klaas.nebuhr@gmail.com"

WORKDIR /digicubes

RUN apt-get update \
&& apt-get install apt-utils -y \
&& apt-get install gcc -y \
&& apt-get clean

RUN mkdir -p data

RUN pip install --no-cache-dir wheel
RUN pip install --upgrade pip
#COPY dist/*.whl .
#RUN pip install --no-cache-dir digicubes_server-0.1.11-py3-none-any.whl
RUN pip install digicubes-server

EXPOSE 3000/tcp

ENV DIGICUBES_DATABASE_URL sqlite://data/digicubes.db
ENV DIGICUBES_SECRET b3j6casjk7d8szeuwz00hdhuw4ohwDu9o

VOLUME /digicubes/data

CMD ["digicubes-server", "run"]
