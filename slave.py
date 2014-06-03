from flask import Flask
app = Flask(__name__)

from sync_utilities import rsync_call, rsync_call_nonblocking


@app.route('/sync_from_master/', methods=['GET', ])
def sync_project_from_upstream():
    details = request.json
    project = details['project']
    host = details['host']
    source = details['source']
    
    full_source = project + '@' + host + '::' + source

    print "Syncing up " + project

    ## Todo: Enable actualy syncing after testing other parts.
    # rsync_call_nonblocking(full_source, dest, password)


if __name__ == "__main__":
    app.debug = True
    app.run(use_reloader=False)

