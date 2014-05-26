import requests
import simplejson as json

url = "http://localhost:5000/add_project/"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

data = {
 "project": "ubuntu",
 "source": "documents",                              # rsync module
 "host": "xlstosql.brightants.com",
 "dest": "/home/pranjal/projects/osl/arrays/1",      # "/data/ftp/.1/",
 "rsync_password": "iitbhu123",
 "minute": "*/3",
 "start_date": "2014-05-7 18:00",                    # $ date "+%Y-%m-%d %H:%M"
}

r = requests.post(url, data=json.dumps(data), headers=headers)

