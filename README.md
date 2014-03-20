Open Source Lab: Simple Mirror Syncing API
------------------------------------------

The following functionality is being built at the moment:

* Adding projects

### Adding an upstream project

Projects are added via the api. The following parameters are specified:

* Project name
* Host IP
* Source (Absolute path on the host used to pull content)
* Destination (Path on the master where the
* interval_unit: {minutes, hours or days}
* interval_value: an integer
* start_date in posix format Eg: "2014-03-10 09:30"


### Geting up and running

    virtualenv venv
    pip install -r requirements.txt
    python main.py

    # This starts the local api server (in development mode)


### Examples:

#### Adding a project:

Send a `POST` request to of content-type `application/json` type to:

    http://127.0.0.1:5000/addproject/

Example of a JSON request for adding a project:

        {
         "project": "fedora",
         "source": "/ftp/package",
         "host": "rsync.fedora.org",
         "dest": "/data/ftp/.1/",
         "rsync_password": "testpassword",
         "interval": "1",
         "interval_unit": "minutes"
        }

The following response is returned if adding project is successful:

        {
         method: "add_project"
         project: "fedora"
         success: true
        }

