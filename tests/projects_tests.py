#!/usr/bin/env python

from apscheduler.triggers.cron import CronTrigger

import base64
from datetime import datetime
from dateutil.parser import parse
import json

from . import MsyncApiTestCase
from flask import url_for
from settings import ROOT_USER, ROOT_PASS
from master.models import User

import unittest

def sync_project_from_upstream(project, rsync_host, rsync_module, dest, rsync_password,
                               rsync_options):
    """
    Does a lot of work in the main app. But here, lets just say its  just a simple
    print for testing.
    """
    print("Imaginary syncing of project complete")


class ProjectsTestCase(MsyncApiTestCase):

    def add_test_project(self):
        """
        Add project to scheduler as well as db.
        Dont use api endpoint to add a project since we shouldn't ideally
        use one api endpoint to test the other.
        """
        job_id = 'ubuntu'  # Same as name of project
        job_kwargs = {'project': 'ubuntu',
                      'rsync_host': 'rsync.osuosl.org',
                      'rsync_module': 'all',
                      'dest': '/home/osl/ftp/1/',
                      'rsync_password': 'rsync_pass',
                      'rsync_options': {},}

        job_kwargs['rsync_options']['basic'] = []
        job_kwargs['rsync_options']['defaults'] = self.app.config['RSYNC_DEFAULT_OPTIONS']
        job_kwargs['rsync_options']['delete'] = self.app.config['RSYNC_DELETE_OPTION']
        schedule_kwargs = {'minute': '*/5',}
        schedule_kwargs['start_date'] = parse('15th August 2014', fuzzy=True)
        # Add the job to the already running scheduler
        ct = CronTrigger(**schedule_kwargs)
        job = self.scheduler.add_job(func=sync_project_from_upstream, id=job_id, trigger=ct, kwargs=job_kwargs)

    def test_list_projects(self):
        self.add_test_project()
        print self.scheduler.get_jobs()

        response = self.open_with_auth('list_projects/', 'GET', ROOT_USER, ROOT_PASS)
        #response = self.client.get(url_for('list_projects'))
        #                           headers=[('Authorization', 'Basic '
        #                                     + base64.b64encode(ROOT_USER +
        #                                                        ':' +
        #                                                        ROOT_PASS))])
        print response.data
        self.assert_200(response)

        #XXX Remove temp code that acts as example.
        #users = (response.json)['users']
        #usernames = [user['username'] for user in users]

        #self.assertIn(ROOT_USER, usernames, 'root not in user list')
        #self.assertIn(self.test_user, usernames, 'test_user not in user list')
        #self.assertEqual(2, len(usernames), 'unexpected number of users')


if __name__ == '__main__':
    unittest.main()
