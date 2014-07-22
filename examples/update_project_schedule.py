import requests
from requests.auth import HTTPBasicAuth
import simplejson as json

url = "http://localhost:5000/update_project/schedule/"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# To  update multiple parameters at once.
data = {
 "id": "ubuntu",
 "minute": "*/5",
 "start_date": "2014-05-7 18:00",                    # $ date "+%Y-%m-%d %H:%M"
}

r = requests.post(url, auth=HTTPBasicAuth('root', 'root'), data=json.dumps(data), headers=headers)

