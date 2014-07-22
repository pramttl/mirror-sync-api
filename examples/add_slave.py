import requests
from requests.auth import HTTPBasicAuth
import simplejson as json

url = 'http://localhost:5000/add_slave/'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

data = {
 'hostname': 'localhost',
 'port': '7000'
}

r = requests.post(url, auth=HTTPBasicAuth('root', 'root'), data=json.dumps(data), headers=headers)

