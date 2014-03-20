from flask import Flask, request, jsonify
app = Flask(__name__)

from apscheduler.scheduler import Scheduler

# Configuring a persistent job store and instantiating scheduler
config = {'apscheduler.jobstores.file.class': 'apscheduler.jobstores.shelve_store:ShelveJobStore',
          'apscheduler.jobstores.file.path': 'scheduledjobs.db'}

sched = Scheduler(config)

def sync_project_from_upstream():
    print "Syncing from upstream!"


@app.route('/addproject/', methods=['POST',])
def add_project():
    '''
    Schedules an upstream project for syncing (periodic)

    @project_name: Name of the project
    @host: IP or hostname of the upstream rsync provider.
    @source_path: Complete path on the source that tells the rsync path.
    '''
    project_name = request.args["name"]
    host = request.args["host"]
    source_path = request.args["source_path"]
    interval_unit = request.args["interval_unit"]
    interval = int(request.args["interval"])
    start_date = request.args["start_date"]

    interval_kwargs = {'start_date': start_date, interval_unit: 2}

    sched.add_interval_job(sync_project_from_upstream, **interval_kwargs)
    sched.start()

    return jsonify({"success": True})

if __name__ == "__main__":
    app.debug = True
    app.run()

