#!/usr/bin/env bash

bash -c "
    cd author-id-model/ &&
        source .env1/bin/activate &&
        python -m app.main
" &
