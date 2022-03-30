# author-id-server
Server that will allow web access to the author-id application

Instructions for use:
```
git clone https://github.com/tafaulhaber590/author-id-server/ --recurse-submodules
cd author-id-server

# Python setup
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt

# Execute main module in debug mode
python -m app.main debug
```

The app will serve on port 8090 by default. This can be changed in the config/config.json file.
