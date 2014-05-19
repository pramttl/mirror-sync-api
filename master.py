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
    action_status = False
    for job in jobs:
        if job.kwargs['project'] == project:
            action_status = True
            sched.unschedule_job(job)
            break

    return jsonify({'method': 'remove_project', 'success': action_status, 'project': project })


@app.route('/update_project/basic/', methods=['POST', ])
def update_project_settings():
    '''
    Updating basic settings of a project scheduled for syncing.
    - Updating name, source, host, dest is allowed.
    - The cron schedule parameters cannot be changed from this endpoint.

    @project: (Required) Orignal name of the project.
    @new_name: (Optional) New name of the project.
    Other parameters are same as in add_project endpoint.
    '''
    project_obj = request.json

    # If there is any new project name then use it else use the old project name.
    updated_name = project_obj.get('new_name') or project_obj["project"]

    # Finding the earlier job and removing it.
    jobs = sched.get_jobs()
    action_status = False
    for job in jobs:
        if job.kwargs['project'] == project_obj["project"]:
            job.kwargs['project'] = updated_name
            job.kwargs['host'] = project_obj.get('host') or job.kwargs['host']
            job.kwargs['source'] = project_obj.get('source') or job.kwargs['source']
            job.kwargs['dest'] = project_obj.get('dest') or job.kwargs['dest']
            job.kwargs['password'] = project_obj.get('rsync_password') or job.kwargs['rsync_password']
            break

    return jsonify({'method': 'update_project', 'success': action_status, 'project': updated_name })


@app.route('/update_project/schedule/', methods=['POST', ])
def update_project_schedule():
    '''
    To update the schedule parameters while updating a project.

    Rule: Specify all the schedule parameters again while updating. The previous
    schedule parameters will be overwritten.

    The only way to update the schedule parameters in Apscheduler v2 is to delete
    the job and add it again with the new parameters. (Apscheduler v3 should have a
    direct way to do this)
    '''
    project_obj = request.json

    # If there is any new project name then use it else use the old project name.
    project = project_obj["project"]

    # Finding the earlier job and removing it.
    jobs = sched.get_jobs()
    action_status = False
    for job in jobs:
        if job.kwargs['project'] == project_obj["project"]:
            sched.unschedule_job(job)
            break

    print job
    # The variable `job` still holds the basic parameters of the job being updated.

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

    action_status = True

    logging.basicConfig()

    # Add the job to the already running scheduler
    sched.add_cron_job(sync_project_from_upstream, kwargs=job.kwargs, **schedule_kwargs)

    return jsonify({'method': 'update_project', 'success': action_status, 'project': project })


if __name__ == "__main__":
    app.debug = True
    app.run(use_reloader=False)

