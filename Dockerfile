FROM ubuntu:16.04

MAINTAINER JordSti, https://github.com/jordsti/MusicBot

#Install dependencies
RUN sudo apt-get update \
    && sudo apt-get install software-properties-common -y \
    && sudo apt-get update -y \
    && sudo apt-get install build-essential unzip -y \
    && sudo apt-get install python3 python3-pip

#Add musicBot
ADD . /musicbot
WORKDIR /musicbot

#Install PIP dependencies
RUN sudo pip install -r requirements.txt

#Add volume for configuration
VOLUME /musicbot/config

CMD python3 run.py
