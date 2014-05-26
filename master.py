from apscheduler.scheduler import Scheduler
from apscheduler.triggers import CronTrigger

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import settings
import simplejson as json
from sync_utilities import rsync_call, rsync_call_nonblocking

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

LOG_FILE = "logfile.txt"
import logging

##################### SCHEDULER STARTUP #########################
# Configuring a persistent job store and instantiating scheduler
# Scheduler starts along with the app.
config = {
    'apscheduler.jobstores.file.class': 'apscheduler.jobstores.shelve_store:ShelveJobStore',
    'apscheduler.jobstores.file.path': 'scheduledjobs.db'
}

sched = Scheduler(config)
sched.start()


############################  MODELS  #############################
class SlaveNode(db.Model):
    '''
    Model that contains data related to FTP Host or slave that syncs
    from the master.
    '''
    __tablename__ = 'slaves'
    id = db.Column('slave_id', db.Integer, primary_key=True)
    hostname = db.Column(db.String(60))
    port = db.Column(db.String)

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port


####################### UTILITY FUNCTIONS ########################
def sync_project_from_upstream(project, host, source, dest, password):
    full_source = project + '@' + host + '::' + source

    print "Syncing up " + project
    rsync_call(full_source, dest, password)

    # Tell all ftp hosts to sync from the master


######################### API ENDPOINTS ##########################
@app.route('/add_slave/', methods=['POST', ])
def add_slave():
    '''
    Add a slave node or ftp host to the the FTP setup.
    '''
    obj = request.json
    ftp_host = SlaveNode(obj["hostname"], obj["port"])
    db.session.add(ftp_host)
    db.session.commit()
    return jsonify({'method': 'add_slave', 'success': True, 'hostname': hostname })


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
    sched.add_cron_job(sync_project_from_upstream, kwargs=job_kwargs,
                       **schedule_kwargs)

    return jsonify({'method': 'add_project', 'success': True, 'project': project })


@app.route('/list_projects/', methods=['GET', ])
def list_projects():
    '''
    List all the upstream projects scheduled for syncing.
    '''
    jobs = sched.get_jobs()
    projects = []
    for job in jobs:

        schedule_dict = dict(zip(CronTrigger.FIELD_NAMES, job.trigger.fields))
        keys = schedule_dict.keys()
        values = map(str, schedule_dict.values())
        cleaned_schedule_dict = dict(zip(keys, values))
        # Add cron parameters of the job along with the other parameters.
        for key,value in schedule_dict.items():
            job.kwargs['cron'] = cleaned_schedule_dict

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

    return jsonify({'method': 'remove_project', 'success': action_status,
                    'project': project })


@app.route('/syncup/', methods=['GET', ])
def syncup_project():
    '''
    Allows to explicitly initiate syncing for a project.
    '''
    project = request.args.get('project')

    if project:
        jobs = sched.get_jobs()
        action_status = False
        for job in jobs:
            if job.kwargs['project'] == project:
                break

        host = job.kwargs['host']
        source = job.kwargs['source']
        project = job.kwargs['project']
        dest = job.kwargs['dest']
        password = job.kwargs['password']

        full_source = project + '@' + host + '::' + source
        rsync_call_nonblocking(full_source, dest, password)

        return jsonify({'method': 'syncup_project', 'success': True,
                        'project': project, 'note': 'sync initiated'})
    else:
        return jsonify({'method': 'syncup_project', 'success': False,
                        'project': project, 'note': 'No project name provided'})


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

    return jsonify({'method': 'update_project', 'success': action_status,
                    'project': updated_name })


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

    return jsonify({'method': 'update_project', 'success': action_status,
                    'project': project })


if __name__ == "__main__":
    app.debug = True
    app.run(use_reloader=False)

