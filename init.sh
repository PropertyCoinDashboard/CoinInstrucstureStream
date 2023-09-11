#!/bin/bash 

echo "kafka streaming initalization"
echo "현재 경로 --> " $(pwd)

cd pipe
python3 async_coin_kafka.py