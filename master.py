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
    full_source = project + '@' + host + '::' + source

    print "Running scheduled sync of " + project
    rsync_call(full_source, dest, password)


@app.route('/add_project/', methods=['POST', ])
def add_project():
    '''
    Schedules an upstream project for syncing (periodic)

    @project: Name of the unix user of the upstream project server
    @host: IP or hostname of the upstream rsync provider
    @source: Complete path on the source that tells the rsync path
    '''
    project_obj = request.json
    project = project_obj["project"]

    job_kwargs = {'project': project,
                  'host': project_obj['host'],
                  'source': project_obj['source'],
                  'dest': project_obj['dest'],
                  'password': project_obj['rsync_password'],}

    # Reading the schedule parameters into a separate dictionary
    schedule_kwargs = {}

    # This is to make sure that default APScheduler values are not overwritten by None
    if project_obj.get('start_date'):
        schedule_kwargs['start_date'] = project_obj.get('start_date')

    if project_obj.get('month'):
        schedule_kwargs['month'] = project_obj.get('month')

    if project_obj.get('day'):
        schedule_kwargs['day'] = project_obj.get('day')

    if project_obj.get('hour'):
        schedule_kwargs['hour'] = project_obj.get('hour')

    if project_obj.get('minute'):
        schedule_kwargs['minute'] = project_obj.get('minute')

    if project_obj.get('day_of_week'):
        schedule_kwargs['day_of_week'] = project_obj.get('day_of_week')

    logging.basicConfig()

    # Add the job to the already running scheduler
    sched.add_cron_job(sync_project_from_upstream, kwargs=job_kwargs, **schedule_kwargs)

    return jsonify({'method': 'add_project', 'success': True, 'project': project })


@app.route('/list_projects/', methods=['GET', ])
def list_projects():
    '''
    List all the upstream projects scheduled for syncing.
    '''
    jobs = sched.get_jobs()
    projects = []
    for job in jobs:
        projects.append(job.kwargs)
    print projects
    return json.dumps(projects)


@app.route('/remove_project/', methods=['POST', ])
def remove_project():
    '''
    Remove an upstream project from the master node.
    '''
    project_obj = request.json
    project = project_obj['project']

    jobs = sched.get_jobs()
    for job in jobs:
        if job.kwargs['project'] == project:
            print "Job found"
            sched.unschedule_job(job)

    return jsonify({'method': 'remove_project', 'success': True, 'project': project })


if __name__ == "__main__":
    app.debug = True
    app.run(use_reloader=False)

