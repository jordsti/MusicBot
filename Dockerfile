FROM ubuntu:16.04

MAINTAINER JordSti, https://github.com/jordsti/MusicBot
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

#Install dependencies
RUN apt-get update \
    && apt-get install software-properties-common -y \
    && apt-get update -y \
    && apt-get install build-essential unzip -y \
    && apt-get install python3 python3-pip -y
RUN apt-get install ffmpeg libopus-dev libffi-dev libmysqlclient-dev -y
#RUN locale-gen "en_US.UTF-8"
#RUN dpkg-reconfigure locales
#RUN echo "export LC_ALL=en_US.utf8" >> ~/.bashrc
#RUN echo "export LANG=en_US.utf8" >> ~/.bashrc RUN echo "export LANGUAGE=en_US.utf8" >> ~/.bashrc

#Add musicBot
ADD . /musicbot
WORKDIR /musicbot

#Install PIP dependencies
RUN pip3 install -r requirements.txt
RUN pip3 install mysqlclient

#Add volume for configuration
VOLUME /musicbot/config

CMD python3 run.py
