#!/bin/bash

mkdir -p config

echo "{
    \"port\": 5001,
    \"modelServerPort\": 5000
}" > config/config.json