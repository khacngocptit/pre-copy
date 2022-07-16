import requests
import json
import os
path = os.listdir("/home/ec2-user/preschooler-menu/Menu/mam-non/5/30000")
# print(path)
url = "http://localhost:3000/khau-phan-an/internal"
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
}
for i in path:
    print(i)
    path_file = "/home/ec2-user/preschooler-menu/Menu/mam-non/5/30000/"+ i 
    print(path_file)
    f = open(path_file)
    data = json.load(f)
    payload = json.dumps(data)
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
