from flask.ext.testing import TestCase
from flask import Flask
from master.models import db
from master import master as app
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

##################### TEST SCHEDULER CONFIG #########################
jobstores = {
    'default': MemoryJobStore(),
    # This is different from non-test jobstore in that it is non-persistent.
}

executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = BackgroundScheduler()

def init_db(app, db):
    with app.app_context():
        db.create_all(app=app)
        # Create root user if it does not exist.
        root_user = User.query.filter_by(username=app.config['ROOT_USER']).first()
        if not root_user:
            root_user = User(app.config['ROOT_USER'], app.config['ROOT_PASS'], 'root')
            db.session.add(root_user)
            db.session.commit()


class MsyncApiTestCase(TestCase):

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['ROOT_USER'] = 'root'
        app.config['ROOT_PASS'] = 'root'
        app.config['SECRET_KEY'] = 'secret'
        self.app = app
        self.db = db
        self.scheduler = scheduler
        return app

    def setUp(self):
        # Initializing test database
        init_db(self.app, self.db)

        # Initializing test scheduler
        scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
        scheduler.start()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
        del scheduler
