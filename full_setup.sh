#!/usr/bin/env bash

git clone https://github.com/tafaulhaber590/author-id-model/ --recurse-submodules &&
    cd author-id-model &&
    python3 -m venv .env1 &&
    source .env1/bin/activate &&
    ./setup.sh &&
    ./params_get.sh &&
    wget https://github.com/tafaulhaber590/author-id-model/releases/download/checkpoint/model-out.zip &&
    unzip model-out.zip &&
    echo "{
        \"port\": 8080,
        \"debug\": false
    }" > config.json # Debug must be false

cd ..
source .env/bin/activate
