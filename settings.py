import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + PROJECT_ROOT + '/master.db'

####### Master node settings #######
MASTER_HOSTNAME ='localhost'
MASTER_RSYNCD_PASSWORD = 'iitbhu123'
MASTER_RSYNCD_MODULE = 'all1'
MASTER_PORT = 5000

SLAVE_PUBLIC_DIR = '/home/pranjal/projects/osl/slave_node/public_html/'
SLAVE_USER = 'pranjal'
SLAVE_PORT = 7000


####### RSYNC OPTIONS ##########

# List of rsync options that are applied by default unless overrided
RSYNC_DEFAULT_OPTIONS = ['-avH',]

# This rsync delete option is used in all cases unless overrided.
RSYNC_DELETE_OPTION = '--delete'
