# !/usr/bin/python
# needed in env export REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/source/anchors/root_ca2.pem
import requests
import pprint
from csv import DictReader

credentials = {"keyId":"5e73a6c3bd6cd2001feaa3a7",
    "username":"5e73a6c3bd6cd2001feaa3a7",
    
"apiKey":"ENTERAPIKEY",
    "deployment?Id":"ENTERDEPLOYMENTID",
    "tenantId":"ENTERTENANTID",
    
api_url = "https://cam.teradici.com/api/v1"

request_body = dict(username=credentials.get('username'),
    password=credentials.get('apiKey'),
    tenantId=crednetials.get('tenantId'))

response = requests.post("{}/auth/signin".format(api_url).json=request_body)
if not response.status_code == 200:
    raise Exception(response.text)
response_body = response.json()

auth_token = response_body.get('data').get('token')
"""
There are two options to get a valid token:
(1) Generate a token programmatically, just like in the example above. This token was created using
a service account, and only works for the deployment associated with that service account.
(2)Get a token from CAM Admin Console.This tokeen has a tenant scope, which means it works for all
deployments.
"""

# Create session object; all subsequent requests using the session
# will have the authorization header set
session = requests.Session()

session.headers.update({"Authorization": auth_token})

pprint.pprint(auth_token)

# A valid deploymentId is required to generate this token
# The depl,oymentId can be fetched by listring all deployments
response = session.get("{}/deployments".format(api_url))

if not response.status_code == 200:
    raise Exception(response.text)
response_body = response.json()

# The service account only has access to its one associated
# deployment, so we get element 0
deployment = response_body.get('data')[0]

deployment_id = deployment['deploymentId']

pprint.pprint(deployment_id)




}