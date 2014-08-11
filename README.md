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

### Clone project and edit settings

Note: **These steps only needs to be performed during setup**

* Clone the repository on the master node.
* Start an rsync daemon on the master node with an appropriate rsyncd conf file and password.
* Keep only one rsyncd module on the master node. That is not only a requirement, but should be sufficient.
* Edit the settings.py file suitably where parameters like master_hostname, master_rsync_password etc are defined.
* Now copy the repository to each of the nodes (both master and slaves) at any location.

Proceed to next steps.


### Running the master node REST API

    virtualenv venv
    pip install -r requirements.txt
    python master/master.py

    # This starts the local api server (in development mode)


Note: Make sure you edit the settings in `settings.py` file before starting
the master. The settings includes information like *hostname* of the master node.
Rsync daemon password of master node rsync daemon.

Master node API runs on port 5000 by default.

### Running the slave node REST API

On each of the slave nodes start the slave node API.

    python slave/slave.py

Slave Node API runs on port 7000 by default. There should be no need to manually
interact with the slave node API. It is primarily used by the master for inter
system communication.

### Adding a slave node

The master needs to be aware of the hostname of each of the slave node and the port
where slave node API is running, hence adding slave nodes on the master is important.

Send a `POST` request to of content-type `application/json` type to:

    http://127.0.0.1:5000/add_slave/

The POST request should include username and password as per HttpBasicAuth authorization.

Allowed Roles: `root`
(This means only root users are allowed to perform this operation)

Example payload:

    data = {
     'hostname': 'localhost',
     'port': '7000'
    }


### Listing all slave nodes

Just send a `GET` request to `/list_slaves/`
This will list all the slave nodes added on master.

Allowed Roles: `root`

### Removing a slave node

Send a `POST` request to of content-type `application/json` type to:

    http://127.0.0.1:5000/remove_slave/

(Request should provide username and password using basic http authentication)

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
         'rsync_module': '<rsync_module_name>/relative_path',
         'rsync_host': 'rsync.fedora.org',
         'dest': '/data/ftp/.1/',
         'rsync_password': 'testpassword',
         'cron_options': {
           'minute': '*',
           'start_date': '2014-05-7 18:00',
          },
         'rsync_options' : {
           'basic': [],
           'defaults': ['-avH',],
           'delete': '--delete',
          },
        }

The parameter names are self-explanatory.

* `project`: Name of the project.
* `id` (optional): This is set equal to the name of the project by default or can be set explicitly.
* `rsync_host`: Hostname or IP address of the rsync source
* `rsync_module`: Note that this parameter is not just rsync_module name but can
   also be rsync_module + relative path from the module on the host machine.
* `dest`: Destination (Path on the master node where the contents from source
   folder are synced to)
* `start_date` Yes, this is the effective time syncing starts (start time included). If this parameter is not provided syncing is in effect as soon as  project is added. The backend uses fuzzy string parsing to map string to a correct datetime object. Unix date format: Eg. "Fri Jul 11 03:08:57 IST 2014" is perfect as it includes all required info to generate corresponding python datetime object. Even something like "2014-03-10 09:30" is accepable though default timezone is set as UTC as timezone is not explicitly provided.

* `rsync_options`: are the extra rsync args that are provided immediately after
   the rsync command in the standard command line execution. In this API the
   `rsync_options` are divied into 3 parts (that should not contain common
   parameters):

   * `defaults`: The API sets some rsync flags by default. These can be overrided
      by setting this list parameter as a blank list or anything as required.
   * `basic`: Standard list of rsync options.
   * `delete`: There are 7 mutually exclusive delete options in rsync.
      Since only one of them can be used at a time, this parameter is a string.

Each project can have its own set of rsync options. These arguments mean the same as
you would find in the [rsync](http://rsync.samba.org/ftp/rsync/rsync.html) man page.

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
        enabled: true
        rsync_options : {
              'basic': [],
              'defaults': ['-avH',],
              'delete_option': '--delete',
            },
        project: "ubuntu",
        rsync_module: "documents",
        rsync_host: "ftp.osuosl.org",
        password: "password",
      },
      ...
    ]

The above list shows one project. There could be several projects listed in your
case depending on how many you have added.

**enabled** parameter tells whether a project is enabled or disabled.

### Enable/Disable a project

Disabled is synonymous with paused which is denoted by a `false` value of `enabled`
parameter in [project listing](/list_projects/)

`/enable_project/` or `/disable_project/` endpoints can be used providing `id`
of project as a GET parameter to enable or disable a project.

Example:

    http://127.0.0.1:5000/disable_project/id=ubuntu

This will pause the syncing for the project whose id=ubuntu.

### Removing a project

Projects can be removed from the API records, based on their id. To remove a
 project send a `POST` request to of content-type `application/json` type to:

    http://127.0.0.1:5000/remove_project/

Example:

        {
         "id": "fedora",
        }

If a project named `fedora` is present in the jobstore it will be removed, otherwise no action will be performed.
If the project was present and successfully removed, 'success' parameter in the JSON returned will be true,
otherwise it will be false.


### Updating a project

##### 1. Updating Basic Settings

Send a JSON POST request to `http://localhost:5000/update_project/basic/`.
Example json payload:

        data = {
          "id": "ubuntu",                                      # Complusary parameter
          "project": "fedora",
          "rsync_module": "new_module_name",                   # rsync module
          "rsync_host": "<new_ip_or_hostname>",
          "dest": "/home/pranjal/projects/osl/syncedup_temp/", # "/data/ftp/.1/",
        }

`id` paramter is compulsary.
The `project` parameter is optional. If this parameter is update the new id will also change and
automatically set as per the name of the project.

    [Note]: Id of the project changes after this operation if a different `project`
    parameter is provided. Also make sure content-type of the request is `application/json`.

##### 2. Updating Schedule Settings

Send a POST request to `http://localhost:5000/update_project/schedule/`.
Example json payload:

        data = {
         "id": "ubuntu",
         "minute": "*/5",
         "start_date": "2014-05-7 18:00",                    # $ date "+%Y-%m-%d %H:%M"
        }

  [Rule]: The previous schedule parameters will be overwritten by the current schedule parameters.
  You just have to assume that the previous project was not scheduled and apply the correct schedule
  settings while updating.The basic project parameters are not altered.


### Adding API Users

Send a POST request to `/create_api_user/`

Example payload:

        data = {
         'username': 'superman',
         'password': 'S'
        }

Allowed Roles: `root`


### Fetching access token

**Warning**: Token based authentication might be broken currently.

It is possible for users to fetch access token by,

Sending a GET request to `/get_token/`

Allowed Roles: Any (But user should be authenticated)


### Explicitly initiating a sync

**Warning**: This feature is broken right now

You can even request syncing up of a particular project apart from the scheduled syncing
by providing the name of a project. The API endpoint for this is:

    /syncup/?project=<your_project_name>

Note: For explicit syncing the project must already be added via the API previously.

