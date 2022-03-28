#!/usr/bin/env bash

mkdir -p config

echo "{
    \"port\": 5001,
    \"modelServerIP\": \"localhost\",
    \"modelServerPort\": 5000,
    \"tempdir\": \"app/tmp/\"
}" > config/config.json