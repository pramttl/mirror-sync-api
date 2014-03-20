from flask import Flask, request, jsonify
app = Flask(__name__)

from apscheduler.scheduler import Scheduler

# Configuring a persistent job store and instantiating scheduler
config = {'apscheduler.jobstores.file.class': 'apscheduler.jobstores.shelve_store:ShelveJobStore',
          'apscheduler.jobstores.file.path': 'scheduledjobs.db'}

sched = Scheduler(config)


def sync_project_from_upstream(project_name, host, source, dest, interval,
                               rsync_password, start_date):
    # Todo
    '''
    args = ["rsync", "-avz", "--include='*/'", source, dest]
    subprocess.call(args)
    '''
    print "Syncing of " + project_name + " has been scheduled!"


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
    source = request.args["source"]
    dest = request.args["dest"]
    interval_unit = request.args["interval_unit"]
    interval = int(request.args["interval"])
    start_date = request.args["start_date"]
    rsync_password = ""

    interval_kwargs = {'start_date': start_date, interval_unit: 2}

    job_function = lambda: sync_project_from_upstream(project_name,
                                                      host,
                                                      source_path,
                                                      interval,
                                                      start_date)

    sched.add_interval_job(job_function, **interval_kwargs)
    sched.start()

    return jsonify({"success": True})


if __name__ == "__main__":
    app.debug = True
    app.run()

