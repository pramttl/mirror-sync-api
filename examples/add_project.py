import requests
from requests.auth import HTTPBasicAuth
import simplejson as json

url = "http://localhost:5000/add_project/"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

data = {
 "project": "ubuntu",
 "rsync_module": "documents",                              # rsync module
 "rsync_host": "xlstosql.brightants.com",
 "dest": "/home/pranjal/projects/osl/arrays/1",      # "/data/ftp/.1/",
 "rsync_password": "iitbhu123",
 # 'rsync_options': Omitted, default options will be applied.
 "cron_options": {
      "minute": "*",
      "start_date": "2014-05-7 18:00",                # $ date "+%Y-%m-%d %H:%M"
     }
  }

r = requests.post(url, auth=HTTPBasicAuth('root', 'root'), data=json.dumps(data), headers=headers)
print r.text

