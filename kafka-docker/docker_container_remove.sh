#!/bin/bash

sudo rm -rf ./visualization/prometheus/volume
sudo rm -rf ./visualization/prometheus/grafana
sudo rm -rf ./.kafkalogging


mkdir -p ./visualization/prometheus/volume
mkdir -p ./visualization/prometheus/grafana
mkdir -p ./visualization/grafana

sudo chmod -R 777 ./visualization/prometheus/config
sudo chmod -R 777 ./visualization/prometheus/volume
sudo chmod -R 777 ./visualization/grafana

if sudo docker rm -f $(docker ps -aq); then
    echo 모든 컨테이너를 삭제하고 다시 시작합니다
    sudo docker compose -f kafka-compose.yml up --build
else
    echo 삭제할 컨테이너가 없습니다 컨테이너 시작합니다 
    sudo docker compose -f kafka-compose.yml up --build
    exit 1
fi


