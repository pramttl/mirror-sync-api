#!/usr/bin/env python

import unittest
import base64
import json
from . import MsyncApiTestCase
from flask import url_for
from settings import ROOT_USER, ROOT_PASS
from master.models import User

class ProjectsTestCase(MsyncApiTestCase):

    def add_test_project(self):
        print("Todo: Add project to scheduler as well as db")
        # Add project to scheduler as well as db.
        # Dont use api endpoint to add a project since we shouldn't ideally
        # use one api endpoint to test the other.

    def test_list_projects(self):
        self.add_test_project()

        response = self.open_with_auth('/list_projects/', 'GET', ROOT_USER, ROOT_PASS)
        #print response.data
        self.assert_200(response)

        #XXX Remove temp code that acts as example.
        #users = (response.json)['users']
        #usernames = [user['username'] for user in users]

        #self.assertIn(ROOT_USER, usernames, 'root not in user list')
        #self.assertIn(self.test_user, usernames, 'test_user not in user list')
        #self.assertEqual(2, len(usernames), 'unexpected number of users')


if __name__ == '__main__':
    unittest.main()
