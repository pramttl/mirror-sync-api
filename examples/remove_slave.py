import requests
from requests.auth import HTTPBasicAuth
import simplejson as json

url = "http://localhost:5000/remove_slave/"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

data = {
 'hostname': 'localhost',
}

r = requests.post(url, auth=HTTPBasicAuth('root', 'root'), data=json.dumps(data), headers=headers)

