import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from flask import Flask, request, jsonify
app = Flask(__name__)
app.config.from_object('settings')

import requests
from utils.syncing import rsync_call, rsync_call_nonblocking
import settings
import simplejson as json

# Every slave api instance can have only one master host at a time
master_hostname = app.config['MASTER_HOSTNAME']
master_port = app.config['MASTER_PORT']

####################### UTILITY FUNCTIONS ########################

def inform_master_sync_complete(slave_id, project):
    """
    Informs the relevant master API endpoint that the slave has completed sync
    for xyz project.
    """
    url = 'http://%s:%s/slave_rsync_complete/'%(master_hostname, str(master_port))
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {
     'slave_id': slave_id,
     'project': project,
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)


######################### API ENDPOINTS ##########################

@app.route('/sync_from_master/', methods=['POST', ])
def sync_project_from_upstream():
    """
    An API endpoint that is used by the master to tell the
    slave nodes to sync from it.
    """
    details = request.json

    # source = details['source']
    project = details['project']
    rsync_password = details['rsync_password']
    rsync_options = details['rsync_options']
    slave_id = details['slave_id']
    full_source = '%s@%s::%s/%s' % (app.config['SLAVE_USER'], master_hostname, \
                                  app.config['MASTER_RSYNCD_MODULE'], project)

    print('I am syncing up -%s- using rsync source: %s' % (project, full_source,))

    dest = app.config['SLAVE_PUBLIC_DIR']

    # Pull the data from the master node via rsync
    rsync_call_nonblocking(full_source, dest, rsync_password,
                           rsync_options['basic'],
                           rsync_options['defaults'],
                           rsync_options['delete'],)

    print('I have completed syncing of -%s- from master node' % (project,))

    # As soon as rsync completes we could hit another endpoint on the master
    # node to inform it that *so and so* slave node has completed rsync.
    inform_master_sync_complete(slave_id, project)

    return jsonify({'success': True, 'details': 'Rsync call initiated on all slave nodes' })


if __name__ == "__main__":
    app.debug = True
    #autoregister_to_master()
    app.run(port=app.config['SLAVE_PORT'], use_reloader=False)
