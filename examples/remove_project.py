import requests
import simplejson as json

url = "http://localhost:5000/remove_project/"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

data = {
 "project": "ubuntu",
}

r = requests.post(url, data=json.dumps(data), headers=headers)

