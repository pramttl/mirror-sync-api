#!/usr/bin/env python

from flask import Flask
from flask.ext.script import Manager
from sqlalchemy import create_engine

app = Flask(__name__)
app.config.from_object('config')
manager = Manager(app)

import master
