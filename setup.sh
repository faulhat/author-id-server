#!/bin/bash

cp win95.css/ app/static/ -r

mkdir -p config

echo "{
    \"port\": 5001,
    \"modelServerPort\": 5000
}" > config/config.json