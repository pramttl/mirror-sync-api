from flask import Flask, request, jsonify
app = Flask(__name__)

from apscheduler.scheduler import Scheduler
LOG_FILE = "logfile.txt"

# Configuring a persistent job store and instantiating scheduler
config = {'apscheduler.jobstores.file.class': 'apscheduler.jobstores.shelve_store:ShelveJobStore',
          'apscheduler.jobstores.file.path': 'scheduledjobs.db'}

sched = Scheduler(config)

# Scheduler starts along with the app.
sched.start()

import logging


def sync_project_from_upstream(project, host, source, dest,
                               rsync_password, start_date):
    # Todo
    '''
    args = ["rsync", "-avz", "--include='*/'", source, dest]
    subprocess.call(args)
    '''
    print "Syncing of " + project + " has been scheduled!"


@app.route('/addproject/', methods=['POST',])
def add_project():
    '''
    Schedules an upstream project for syncing (periodic)

    @project: Name of the project
    @host: IP or hostname of the upstream rsync provider.
    @source_path: Complete path on the source that tells the rsync path.
    '''
    project = request.form["project"]
    host = request.form["host"]
    source = request.form["source"]
    dest = request.form["dest"] or "/data/ftp/.1"
    interval_unit = request.form["interval_unit"] or "minutes"
    interval = int(request.form["interval"])
    start_date = request.args["start_date"] or None
    rsync_password = ""

    job_function = lambda: sync_project_from_upstream(project,
                                                      host,
                                                      source_path,
                                                      interval,
                                                      start_date)

    if start_date:
        interval_kwargs = {"start_date": start_date, interval_unit: interval}
    else:
        interval_kwargs = {"start_date": start_date, interval_unit: interval}

    logging.basicConfig()

    # Add the job to the already running scheduler.
    sched.add_interval_job(job_function, **interval_kwargs)

    return jsonify({"success": True})


if __name__ == "__main__":
    app.debug = True
    app.run()

