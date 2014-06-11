from apscheduler.scheduler import Scheduler
from apscheduler.triggers import CronTrigger

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import requests
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
# Scheduler starts along with the app (just before)
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

    @property
    def to_dict(self):
       """Converts SlaveNode object to a dictionary"""
       return {
           'id': self.id,
           'hostname': self.hostname,
           'port': self.port,
       }


####################### UTILITY FUNCTIONS ########################
def sync_project_from_upstream(project, rsync_host, rsync_module, dest, password,
                               rsync_options):
    '''
    Sync's project from upstream and after upstream-master syncing is over,
    instructs each of the slave nodes to sync from the master.

    Note: The same rsync_options are used for upstream-master syncing as for
    the master-slave syncing.
    '''
    full_source = project + '@' + rsync_host + '::' + rsync_module
    dest = dest + '/' + project

    print "Syncing up " + project

    # Blocking rsync call
    rsync_call(full_source, dest, password, rsync_options)

    ftp_hosts = SlaveNode.query.all()
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    # Tell all ftp hosts to sync from the master
    for node in ftp_hosts:
        slave_api_url = 'http://' + node.hostname + ':' + node.port + '/sync_from_master/'
        data = {
         "project": project,
          #"rsync_module": settings.MASTER_RSYNCD_MODULE + '/' + project, # rsync module
         "rsync_host": settings.MASTER_HOSTNAME,
         "rsync_password": settings.MASTER_RSYNCD_PASSWORD,
         "rsync_options" : rsync_options,
          }

        # Slave api rsync should be non blocking so that this call returns immediately.
        r = requests.post(slave_api_url, data=json.dumps(data), headers=headers)

        # Analyze respone

######################### API ENDPOINTS ##########################
@app.route('/add_slave/', methods=['POST', ])
def add_slave():
    '''
    Add a slave node or ftp host to the the FTP setup.
    '''
    obj = request.json
    slave_node = SlaveNode.query.filter(SlaveNode.hostname == obj["hostname"]).first()

    if slave_node:
        details = 'Already added'
    else:
        ftp_host = SlaveNode(obj['hostname'], obj['port'])
        db.session.add(ftp_host)
        db.session.commit()
        details = 'Added to cluster'
    

    return jsonify({'method': 'add_slave', 'success': True, 
                    'hostname': obj['hostname'],
                    'details': details })


@app.route('/list_slaves/', methods=['GET', ])
def list_slaves():
    '''
    Returns a list of all slave objects in JSON format.
    '''
    ftp_hosts = SlaveNode.query.all()
    ftp_hosts = [obj.to_dict for obj in ftp_hosts]
    return json.dumps(ftp_hosts)


@app.route('/remove_slave/', methods=['POST', ])
def remove_slave():
    '''
    Remove a slave node from the ftp cluster.
    '''
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
    '''
    Schedules an upstream project for syncing (periodic)

    @project: Name of the unix user of the upstream project server
    @rsync_host: IP or hostname of the upstream rsync provider
    @rsync_module: <rsync_module_name>/relative_path_from_there
    '''
    project_obj = request.json
    project = project_obj["project"]

    job_kwargs = {'project': project,
                  'rsync_host': project_obj['rsync_host'],
                  'rsync_module': project_obj['rsync_module'],
                  'dest': project_obj['dest'],
                  'password': project_obj['rsync_password'],
                  'rsync_options': project_obj["rsync_options"],}

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
        job_kwargs_copy = job.kwargs.copy()

        # Add cron parameters of the job along with the other parameters.
        for key,value in schedule_dict.items():
            job_kwargs_copy['cron_options'] = cleaned_schedule_dict

        # The copy stores the basic parameters as well as the schedule parameters.
        projects.append(job_kwargs_copy)
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

        rsync_host = job.kwargs['rsync_host']
        rsync_module = job.kwargs['rsync_module']
        project = job.kwargs['project']
        dest = job.kwargs['dest'] + '/' + project
        password = job.kwargs['password']
        rsync_options = project_obj["rsync_options"]

        full_source = project + '@' + rsync_host + '::' + rsync_module
        rsync_call_nonblocking(full_source, dest, password, rsync_options)

        return jsonify({'method': 'syncup_project', 'success': True,
                        'project': project, 'note': 'sync initiated'})
    else:
        return jsonify({'method': 'syncup_project', 'success': False,
                        'project': project, 'note': 'No project name provided'})


@app.route('/update_project/basic/', methods=['POST', ])
def update_project_settings():
    '''
    Updating basic settings of a project scheduled for syncing.
    - Updating name, rsync_module, rsync_host, dest is allowed.
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
            job.kwargs['rsync_host'] = project_obj.get('rsync_host') or job.kwargs['rsync_host']
            job.kwargs['rsync_module'] = project_obj.get('rsync_module') or job.kwargs['rsync_module']
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
    db.create_all()
    app.debug = True
    app.run(use_reloader=False)

