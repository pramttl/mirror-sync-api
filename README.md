Proof of concept of mirror syncing API
--------------------------------------

This repostiory is an experimental proof of concept of an API that writes to
configuration files. To setup do the following steps:

    virtualenv venv
    pip install -r requirements.txt
    python main.py

    # This starts the local development api server


####  Visit

http://localhost:5000/json/sections

This lists all the sections of the `rsyncd-osl.conf` file as a json response.
This file is available in the root directory of this repository.

Further, to add more configuration to an existing rsync module visit
the following:

    localhost:5000/addparam/?module=all&key=testkey&value=testvalue

The `rsyncd-osl.conf` in the root directory is modified with the new key and
value added to the file. There are some issues with writing the global section
that will be corrected.

