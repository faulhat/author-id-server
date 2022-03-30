#!/usr/bin/env bash

git clone https://github.com/tafaulhaber590/author-id-model/ --recurse-submodules &&
    cd author-id-model &&
    python3 -m venv .env &&
    source .env/bin/activate &&
    ./setup.sh &&
    ./params_get.sh &&
    wget https://github.com/tafaulhaber590/author-id-model/releases/download/checkpoint/model-out.zip &&
    unzip model-out.zip &&
    echo "{
        \"port\": 8080,
        \"debug\": false
    }" > config.json &&
    cd .. &&
    source .env/bin/activate
