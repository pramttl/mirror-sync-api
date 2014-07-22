import requests
from requests.auth import HTTPBasicAuth
import simplejson as json

url = "http://localhost:5000/create_api_user/"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

data = {
 'username': 'superman',
 'password': 'iitbhu123'
}

r = requests.post(url, auth=HTTPBasicAuth('root', 'root'), data=json.dumps(data), headers=headers)
print r.text

