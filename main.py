from flask import Flask, request, jsonify
app = Flask(__name__)

import simplejson as json
from sync_utilities import rsync_call

from apscheduler.scheduler import Scheduler
LOG_FILE = "logfile.txt"

# Configuring a persistent job store and instantiating scheduler
config = {'apscheduler.jobstores.file.class': 'apscheduler.jobstores.shelve_store:ShelveJobStore',
          'apscheduler.jobstores.file.path': 'scheduledjobs.db'}

sched = Scheduler(config)

# Scheduler starts along with the app.
sched.start()

import logging


def sync_project_from_upstream(project, host, source, dest, password):
    final_dest = project + '@' + host + '::' + dest

    # rsync_call(source=".", full_dest, password=rsync_password)

    print "Syncing of " + project + " has been scheduled!"


@app.route('/addproject/', methods=['POST', ])
def add_project():
    '''
    Schedules an upstream project for syncing (periodic)

    @project: Name of the project
    @host: IP or hostname of the upstream rsync provider.
    @source: Complete path on the source that tells the rsync path.
    '''
    project_obj = request.json
    project = project_obj["project"]

    print project_obj

    job_function = lambda: sync_project_from_upstream(project,
                                                      project_obj["host"],
                                                      project_obj["source"],
                                                      project_obj["dest"],
                                                      project_obj["rsync_password"])

    start_date = project_obj.get("start_date")
    interval = int(project_obj.get("interval")) or 1
    interval_unit = project_obj.get("interval_unit", "minutes")

    if start_date:
        interval_kwargs = {"start_date": start_date, interval_unit: interval}
    else:
        interval_kwargs = {"start_date": start_date, interval_unit: interval}

    logging.basicConfig()

    # Add the job to the already running scheduler.
    sched.add_interval_job(job_function, **interval_kwargs)

    return jsonify({'method': 'add_project', 'success': True, "project": project})


if __name__ == "__main__":
    app.debug = True
    app.run()
