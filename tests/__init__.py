from flask.ext.testing import TestCase
from flask import Flask
from master.models import db
from master import master as app

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
        return app

    def setUp(self):
        init_db(self.app, self.db)

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
