import requests
import simplejson as json

url = "http://localhost:5000/update_project/basic/"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# To  update multiple parameters at once except schedule parameters.
data = {
 "project": "ubuntu",
 "new_name": "fedora",
 "source": "new_module_name",                         # rsync module
 "host": "xlstosql.brightants.com",
 "dest": "/home/pranjal/projects/osl/syncedup_temp/", # "/data/ftp/.1/",
}

r = requests.post(url, data=json.dumps(data), headers=headers)

