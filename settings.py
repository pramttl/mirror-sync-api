import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + PROJECT_ROOT + '/master.db'

####### Master node settings #######
MASTER_HOSTNAME ='localhost'
MASTER_RSYNCD_PASSWORD = 'iitbhu123'
MASTER_RSYNCD_MODULE = 'all1'

SLAVE_PUBLIC_DIR = '/home/pranjal/projects/osl/slave_node/public_html/'
SLAVE_USER = 'pranjal'

