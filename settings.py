import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + PROJECT_ROOT + '/master.db'

####### Master node settings #######
MASTER_RSYNCD_PASSWORD = 'iitbhu123'
MASTER_HOSTNAME ='localhost'

