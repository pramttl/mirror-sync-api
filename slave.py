from flask import Flask, request, jsonify
app = Flask(__name__)

from sync_utilities import rsync_call, rsync_call_nonblocking
import settings


@app.route('/sync_from_master/', methods=['POST', ])
def sync_project_from_upstream():
    '''
    An API endpoint that is used by the master to tell the
    slave nodes to sync from it.
    '''
    details = request.json

    master_host = settings.MASTER_HOSTNAME

    # source = details['source']
    project = details['project']
    rsync_password = details['rsync_password']
    rsync_options = details['rsync_options']
    full_source = settings.SLAVE_USER + '@' + master_host + '::' + \
                  settings.MASTER_RSYNCD_MODULE + '/' + project

    print 'full_source', full_source

    print "Slave syncing up " + project

    dest = settings.SLAVE_PUBLIC_DIR

    # Pull the data from the master node via rsync
    rsync_call_nonblocking(full_source, dest, rsync_password,
                           rsync_options.get('basic', []),
                           rsync_options.get('defaults', settings.RSYNC_DEFAULT_OPTIONS),
                           rsync_options.get('delete', settings.RSYNC_DELETE_OPTION))

    # As soon as rsync completes we could hit another endpoint on the master
    # node to inform it that *so and so* slave node has completed rsync.

    return jsonify({'success': True, 'details': 'Rsync call initiated on all slave nodes' })


if __name__ == "__main__":
    app.debug = True
    app.run(port=7000, use_reloader=False)

