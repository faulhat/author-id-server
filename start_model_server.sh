#!/usr/bin/env bash

bash -c "
    cd author-id-model/ &&
        source .env/bin/activate &&
        python -m app.main
" &
