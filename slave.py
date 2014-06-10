from flask import Flask
app = Flask(__name__)

from sync_utilities import rsync_call, rsync_call_nonblocking
import settings


@app.route('/sync_from_master/', methods=['GET', ])
def sync_project_from_upstream():
    '''
    An API endpoint that is used by the master to tell the
    slave nodes to sync from it.
    '''
    details = request.json

    master_host = settings.MASTER_HOSTNAME

    source = details['source']
    project = details['project']
    
    full_source = project + '@' + host + '::' + source

    print "Syncing up " + project

    ## Todo: Enable actualy syncing after testing other parts.
    # rsync_call_nonblocking(full_source, dest, password)
    # As soon as rsync completes we could hit another endpoint on the master
    # node to inform it that *so and so* slave node has completed rsync.


if __name__ == "__main__":
    app.debug = True
    app.run(port=7000, use_reloader=False)

