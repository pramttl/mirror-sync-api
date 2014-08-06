#!/usr/bin/env python

import base64
import json
from . import MsyncApiTestCase
from flask import url_for
from settings import ROOT_USER, ROOT_PASS
from master.models import User

class ProjectsTestCase(MsyncApiTestCase):

    def setUp(self):
        # Login as ROOT_USER prior to all test cases.
        # ROOT_USER should have access to all API endpoints.

        super(MsyncTestCase, self).setUp()
        response = self.client.get(url_for('list_projects'),
                                   headers=[('Authorization', 'Basic '
                                             + base64.b64encode(ROOT_USER +
                                                                ':' +
                                                                ROOT_PASS))])
        self.headers = [('Authorization', 'Basic '
                         + base64.b64encode((response.json)['token']
                         + ':' + ROOT_USER)),]

    def add_test_project(self):
        user = User(self.test_user, self.test_pass)
        self.db.session.add(user)
        self.db.session.commit()
