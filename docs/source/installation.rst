Clone project and edit settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note: **These steps only needs to be performed during setup**

-  Clone the repository on the master node.
-  Start an rsync daemon on the master node with an appropriate rsyncd
   conf file and password.
-  Keep only one rsyncd module on the master node. That is not only a
   requirement, but should be sufficient.
-  Edit the settings.py file suitably where parameters like
   master\_hostname, master\_rsync\_password etc are defined.
-  Now copy the repository to each of the nodes (both master and slaves)
   at any location.

Proceed to next steps.

Note: Care must be taken to ensure the same settings.py file is present in the
repository on all the nodes before running the API daemons.


Running the master node REST API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    virtualenv venv
    pip install -r requirements.txt
    python master/master.py

    # This starts the local api server (in development mode)

Note: Make sure you edit the settings in ``settings.py`` file before
starting the master. The settings includes information like *hostname*
of the master node. Rsync daemon password of master node rsync daemon.

Master node API runs on port 5000 by default. The master API should ideally be
run as a daemon so that it is running even after exiting the shell.


Running the slave node REST API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On each of the slave nodes start the slave node API.

::

    python slave/slave.py

Slave Node API runs on port 7000 by default. There should be no need to
manually interact with the slave node API. It is primarily used by the
master for inter system communication.
