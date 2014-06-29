import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from apscheduler.scheduler import Scheduler
from apscheduler.triggers import CronTrigger

from flask import Flask, request, jsonify, url_for, abort
from database import db

app = Flask(__name__)
app.config.from_object('settings')
db.init_app(app)

import requests
import simplejson as json
from utils.syncing import rsync_call, rsync_call_nonblocking
LOG_FILE = "logfile.txt"
import logging

##################### SCHEDULER STARTUP #########################
# Configuring a persistent job store and instantiating scheduler
# Scheduler starts along with the app (just before)
config = {
    'apscheduler.jobstores.file.class': 'apscheduler.jobstores.shelve_store:ShelveJobStore',
    'apscheduler.jobstores.file.path': 'scheduledjobs.db'
}

sched = Scheduler(config)
sched.start()


############################  MODELS  #############################
from models import User, SlaveNode

####################### UTILITY FUNCTIONS ########################
def sync_project_from_upstream(project, rsync_host, rsync_module, dest, password,
                               rsync_options):
    """
    Sync's project from upstream and after upstream-master syncing is over,
    instructs each of the slave nodes to sync from the master.

    Note: The same rsync_options are used for upstream-master syncing as for
    the master-slave syncing.
    """
    full_source = '%s@%s::%s' % (project, rsync_host, rsync_module)
    dest = '%s/%s' % (dest, project)

    print('Syncing up %s' % (project,))

    # Blocking rsync call
    rsync_call(full_source, dest, password,
               rsync_options.get('basic', []),
               rsync_options.get('defaults', app.config['RSYNC_DEFAULT_OPTIONS']),
               rsync_options.get('delete', app.config['RSYNC_DELETE_OPTION']))

    ftp_hosts = SlaveNode.query.all()
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    # Tell all ftp hosts to sync from the master
    for node in ftp_hosts:
        slave_api_url = 'http://%s:%s/sync_from_master/' % (node.hostname, node.port)
        data = {
         'project': project,
          #"rsync_module": settings.MASTER_RSYNCD_MODULE + '/' + project, # rsync module
         'rsync_host': app.config['MASTER_HOSTNAME'],
         'rsync_password': app.config['MASTER_RSYNCD_PASSWORD'],
         'rsync_options' : rsync_options,
         'slave_id': node.id,
          }

        # Slave api rsync should be non blocking so that this call returns immediately.
        r = requests.post(slave_api_url, data=json.dumps(data), headers=headers)

        # Analyze respone


######################### VIEWS: AUTH X 2  ##############################
@app.route('/test', methods = ['GET'])
def test_function():
    return jsonify({ 'success': True })


@app.route('/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if User.query.filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = User(username = username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username }), 201, \
                   {'Location': url_for('get_user', id = user.id, _external = True)}


######################### VIEWS: API ENDPOINTS ##########################
@app.route('/add_slave/', methods=['POST', ])
def add_slave():
    """
    Add a slave node or ftp host to the the FTP setup.
    """
    obj = request.json
    hostname = obj["hostname"]
    slave_node = SlaveNode.query.filter(SlaveNode.hostname == hostname).first()

    if slave_node:
        details = 'Already added'
        print('Slave already present')
    else:
        ftp_host = SlaveNode(obj['hostname'], obj['port'])
        db.session.add(ftp_host)
        db.session.commit()
        details = 'Added to cluster'
        print('Slave added')

    return jsonify({'method': 'add_slave', 'success': True, 
                    'hostname': obj['hostname'],
                    'details': details })


@app.route('/list_slaves/', methods=['GET', ])
def list_slaves():
    """
    Returns a list of all slave objects in JSON format.
    """
    ftp_hosts = SlaveNode.query.all()
    ftp_hosts = [obj.to_dict for obj in ftp_hosts]
    return json.dumps(ftp_hosts)


@app.route('/remove_slave/', methods=['POST', ])
def remove_slave():
    """
    Remove a slave node from the ftp cluster.
    """
    slave_hostname = request.json['hostname']
    stored_slave = SlaveNode.query.filter(SlaveNode.hostname == slave_hostname).first()
    details = ''

    if stored_slave:
        db.session.delete(stored_slave)
        db.session.commit()
        details = 'Found and deleted'

    return jsonify({'method': 'remove_slave', 'success': True,
                    'details': details })


@app.route('/add_project/', methods=['POST', ])
def add_project():
    """
    Schedules an upstream project for syncing (periodic)

    @project: Name of the unix user of the upstream project server
    @rsync_host: IP or hostname of the upstream rsync provider
    @rsync_module: <rsync_module_name>/relative_path_from_there
    """
    project_obj = request.json
    project = project_obj["project"]

    job_kwargs = {'project': project,
                  'rsync_host': project_obj['rsync_host'],
                  'rsync_module': project_obj['rsync_module'],
                  'dest': project_obj['dest'],
                  'password': project_obj['rsync_password'],
                  'rsync_options': project_obj.get('rsync_options',{}),}

    # Reading the schedule parameters into a separate dictionary
    schedule_kwargs = project_obj['cron_options']

    #Todo: Might need a check to make sure all the sub parameters in the cron
    # parameter are acceptable ie. belong to ['start_date', 'minute', 'hour, ...]

    logging.basicConfig()

    # Add the job to the already running scheduler
    sched.add_cron_job(sync_project_from_upstream, kwargs=job_kwargs,
                       **schedule_kwargs)

    return jsonify({'method': 'add_project', 'success': True, 'project': project })


@app.route('/list_projects/', methods=['GET', ])
def list_projects():
    """
    List all the upstream projects scheduled for syncing.
    """
    jobs = sched.get_jobs()
    projects = []
    for job in jobs:

        schedule_dict = dict(zip(CronTrigger.FIELD_NAMES, job.trigger.fields))
        keys = schedule_dict.keys()
        values = map(str, schedule_dict.values())
        cleaned_schedule_dict = dict(zip(keys, values))
        job_kwargs_copy = job.kwargs.copy()

        # Add cron parameters of the job along with the other parameters.
        for key, value in schedule_dict.items():
            job_kwargs_copy['cron_options'] = cleaned_schedule_dict

        # The copy stores the basic parameters as well as the schedule parameters.
        projects.append(job_kwargs_copy)
    print projects
    return json.dumps(projects)


@app.route('/remove_project/', methods=['POST', ])
def remove_project():
    """
    Remove an upstream project from the master node.
    """
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
                    'project': project})


@app.route('/syncup/', methods=['GET', ])
def syncup_project():
    """
    Allows to explicitly initiate syncing for a project.
    """
    project = request.args.get('project')

    if project:
        jobs = sched.get_jobs()
        for job in jobs:
            if job.kwargs['project'] == project:
                break

        rsync_host = job.kwargs['rsync_host']
        rsync_module = job.kwargs['rsync_module']
        project = job.kwargs['project']
        dest = '%s/%s' % (job.kwargs['dest'], project)
        password = job.kwargs['password']
        rsync_options = project.get('rsync_options')

        full_source = '%s@%s::%s' % (project, rsync_host, rsync_module)
        rsync_call_nonblocking(full_source, dest, password,
                               rsync_options.get('basic', []),
                               rsync_options.get('defaults', app.config['RSYNC_DEFAULT_OPTIONS']),
                               rsync_options.get('delete', app.config['RSYNC_DELETE_OPTION']))

        return jsonify({'method': 'syncup_project', 'success': True,
                        'project': project, 'note': 'sync initiated'})
    else:
        return jsonify({'method': 'syncup_project', 'success': False,
                        'project': project, 'note': 'No project name provided'})


@app.route('/update_project/basic/', methods=['POST', ])
def update_project_settings():
    """
    Updating basic settings of a project scheduled for syncing.
    - Updating name, rsync_module, rsync_host, dest is allowed.
    - The cron schedule parameters cannot be changed from this endpoint.

    @project: (Required) Orignal name of the project.
    @new_name: (Optional) New name of the project.
    Other parameters are same as in add_project endpoint.
    """
    project_obj = request.json

    # If there is any new project name then use it else use the old project name.
    updated_name = project_obj.get('new_name') or project_obj["project"]

    # Finding the earlier job and removing it.
    jobs = sched.get_jobs()
    action_status = False
    for job in jobs:
        if job.kwargs['project'] == project_obj["project"]:
            job.kwargs['project'] = updated_name
            job.kwargs['rsync_host'] = project_obj.get('rsync_host') or job.kwargs['rsync_host']
            job.kwargs['rsync_module'] = project_obj.get('rsync_module') or job.kwargs['rsync_module']
            job.kwargs['dest'] = project_obj.get('dest') or job.kwargs['dest']
            job.kwargs['password'] = project_obj.get('rsync_password') or job.kwargs['rsync_password']
            break

    return jsonify({'method': 'update_project', 'success': action_status,
                    'project': updated_name})


@app.route('/update_project/schedule/', methods=['POST', ])
def update_project_schedule():
    """
    To update the schedule parameters while updating a project.

    Rule: Specify all the schedule parameters again while updating. The previous
    schedule parameters will be overwritten.

    The only way to update the schedule parameters in Apscheduler v2 is to delete
    the job and add it again with the new parameters. (Apscheduler v3 should have a
    direct way to do this)
    """
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
                    'project': project})


@app.route('/slave_rsync_complete/', methods=['POST', ])
def slave_rsync_complete():
    """
    Remove an upstream project from the master node.
    """
    details = request.json
    slave_id = details['slave_id']
    project = details['project']
    slave_node = SlaveNode.query.filter_by(id=slave_id).first()

    #XXX: Register that the slave has synced xyz project to the db.
    print('%s -synced- %s'%(slave_node.hostname, project))

    return jsonify({'method': 'slave_rsync_complete', 'success': True})


if __name__ == "__main__":
    db.create_all(app=app)
    app.debug = True
    app.run(port=app.config['MASTER_PORT'], use_reloader=False)
