Open Source Lab: Simple Mirror Syncing API
------------------------------------------

The following functionality is available (or in progress) at the moment:

**master.py** - Master Node API

* Adding a slave node
* Listing all slave nodes
* Removing a slave node

* Adding an upstream project
* Removing a project
* Updating a project
* Listing all projects

**slave.py** - Slave Node API

(Todo: Only master node API is available at the moment)


### Running the master node REST API

    virtualenv venv
    pip install -r requirements.txt
    python master.py

    # This starts the local api server (in development mode)


Note: Make sure you edit the settings in `settings.py` file before starting
the master. The settings includes information like *hostname* of the master node.
Rsync daemon password of master node rsync daemon.

### Adding a slave node

Send a `POST` request to of content-type `application/json` type to:

    http://127.0.0.1:5000/add_slave/

Example payload:

    data = {
     'hostname': 'localhost',
     'port': '7000'
    }


### Listing all slave nodes

Just send a `GET` request to `/list_slaves/`
This will list all the slave nodes added on master.


### Removing a slave node

Send a `POST` request to of content-type `application/json` type to:

    http://127.0.0.1:5000/remove_slave/

Example Payload:

    data = {
     'hostname': <slave_node_hostname>,
    }


### Adding a project

Send a `POST` request to of content-type `application/json` type to:

    http://127.0.0.1:5000/add_project/

Example payload:

        {
         'project': 'fedora',
         'source': '/ftp/package',
         'host': 'rsync.fedora.org',
         'dest': '/data/ftp/.1/',
         'rsync_password': 'testpassword',
         'cron_options': {
           'minute': '*',
           'start_date': '2014-05-7 18:00',
          },
         'rsync_options' : ['-avH','--delete'],
        }

The parameter names are self-explanatory.

* `project`: Project name
* `host`: Hostname or IP address of the rsync source
* `source`: Source or rsync_module + path (Absolute path on the host used to pull content)
* `dest`: Destination (Path on the master node where the contents from source
   folder are synced to)
* `start_date` in posix format Eg: "2014-03-10 09:30"
* `rsync_options`: are explained ahead. The format is tentative and can be changed
  in subsequent versions of the api.

Each project can have its own set of rsync args. These arguments mean the same as
you would find in the [rsync](http://rsync.samba.org/ftp/rsync/rsync.html) man page.
A list of these arguments is specified in the `rsync_options` paramter.

The following response is returned if adding project is successful:

        {
         method: "add_project"
         project: "fedora"
         success: true
        }

##### Scheduling parameters

The API uses a **cron-like** scheduling as defined in [APScheduler documentation](http://pythonhosted.org/APScheduler/cronschedule.html).
All these scheduling parameters are specfied in the `cron_options` parameter.
Fields greater than the least significant explicitly defined field default to * 
while lesser fields default to their minimum values except for `week` and `day_of_week` which default to *.

Note: Allthough most of these cron-like options are similar to traditional cron
there are a few small differences including extra parameters described in detail
in the above apscheduler page.

Example: A `start_date` can also be specified if required which is the effective time
syncing starts (start time included). If this parameter is not provided syncing 
is in effect as soon as  project is added.. You can obtain a valid start
date by entering the following at bash prompt.

    date "+%Y-%m-%d %H:%M"


### Listing projects

Just send a GET request to the follo. to list all available projects.

    http://127.0.0.1:5000/list_projects/

Example:

    [
      { 
        cron_options: {
          week: "*",
          hour: "*",
          day_of_week: "*",
          month: "*",
          second: "0",
          year: "*",
          day: "*",
          minute: "*"
        },
        dest: "/home/pranjal/projects/osl/syncedup_temp/",
        rsync_options: ["-avH", "--delete"],
        project: "ubuntu",
        source: "documents",
        host: "ftp.osuosl.org",
        password: "password",
      },
      ...
    ]

The above list shows one project. There could be several projects listed in your
case depending on how many you have added.

### Removing a project

Projects can be removed from the API records, based on their name. To remove a
 project send a `POST` request to of content-type `application/json` type to:

    http://127.0.0.1:5000/add_project/

Example:

        {
         "project": "fedora",
        }

If a project named `fedora` is present in the jobstore it will be removed, otherwise no action will be performed.
If the project was present and successfully removed, 'success' parameter in the JSON returned will be true,
otherwise it will be false.


### Updating a project

##### 1. Updating Basic Settings

Send a JSON POST request to `http://localhost:5000/update_project/basic/`.
Example json payload:

        data = {
         "project": "ubuntu",
         "new_name": "fedora",
         "source": "new_module_name",                         # rsync module
         "host": "xlstosql.brightants.com",
         "dest": "/home/pranjal/projects/osl/syncedup_temp/", # "/data/ftp/.1/",
        }

Make sure content-type of the request is `application/json`.

##### 2. Updating Schedule Settings

Send a POST request to `http://localhost:5000/update_project/schedule/`.
Example json payload:

        data = {
         "project": "ubuntu",
         "minute": "*/5",
         "start_date": "2014-05-7 18:00",                    # $ date "+%Y-%m-%d %H:%M"
        }

  [Rule]: The previous schedule parameters will be overwritten by the current schedule parameters.
  You just have to assume that the previous project was not scheduled and apply the correct schedule
  settings while updating.The basic project parameters are not altered.


### Explicitly initiating a sync

You can even request syncing up of a particular project apart from the scheduled syncing
by providing the name of a project. The API endpoint for this is:

    /syncup/?project=<your_project_name>

Note: For explicit syncing the project must already be added via the API previously.
