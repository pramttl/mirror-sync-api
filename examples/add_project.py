import requests
import simplejson as json

url = "http://localhost:5000/addproject/"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

data = {
 "project": "ubuntu",
 "source": "documents",                # module
 "host": "xlstosql.brightants.com",
 "dest": "/home/pranjal/projects/osl/syncedup_temp", # "/data/ftp/.1/",
 "rsync_password": "iitbhu123",
 "interval": "1",
 "interval_unit": "minutes"
}

r = requests.post(url, data=json.dumps(data), headers=headers)

