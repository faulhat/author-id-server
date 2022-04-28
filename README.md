# author-id-server
Server that will allow web access to the author-id application.

A frontend for the author-id-model program (https://github.com/tafaulhaber590/author-id-model), which will be downloaded and set up automatically by the full_setup.sh script.

Build instructions:
```
git clone https://github.com/tafaulhaber590/author-id-server/ --recurse-submodules
cd author-id-server

# Python setup
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt

# Set up model server
./full_setup.sh
```

To run the program:
```
# Execute main module to serve the application
python -m app.main
```

The app will serve on localhost:8090 by default. This can be changed in the config/config.json file. By default a test user will be created when you start the server. You can alter the credentials for this user in that config file as well.

NOTE: If both the `debug` and `doStart` flags are set to `true` in the config file, the program will crash on purpose. This is because the `doStart` flag tells the program to start the author-id-model server, and having two flask servers running in the same shell with either in debug mode will crash. If you are running in debug mode, please run the author-id-model program manually in a separate shell. 
