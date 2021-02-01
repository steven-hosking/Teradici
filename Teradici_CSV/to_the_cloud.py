#!/usr/bin/python
##### needed in env export REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/source/anchors/al_root_ca2.pem
import requests
import pprint
from csv import DictReader

# ENTER YOUR OWN CREDENTIALS 
# credentials = {"keyId":"",
#        "username":"",
#        "apiKey":"",
#        "deploymentId":"",
#        "tenantId":""}

api_url = "https://cam.teradici.com/api/v1"

request_body = dict(username=credentials.get('username'),
                    password=credentials.get('apiKey'),
                    tenantId=credentials.get('tenantId'))

response = requests.post("{}/auth/signin".format(api_url),json=request_body)
if not response.status_code == 200:
    raise Exception(response.text)
response_body = response.json()

auth_token = response_body.get('data').get('token')

"""
There are two options to get a valid token:
(1) Generate a token programmatically, just like in the example above. This token was created using
a service account, and only works for the deployment associated with that service account.
(2) Get a token from CAM Admin Console. This token has a tenant scope, which means it works
for all deployments.
"""

# Create session object; all subsequent requests using the session
# will have the authorization header set
session = requests.Session()

session.headers.update({"Authorization": auth_token})

pprint.pprint(auth_token)

# A valid deploymentId is required to generate this token
# The deploymentId can be fetched by listing all deployments
response = session.get("{}/deployments".format(api_url))

if not response.status_code == 200:
    raise Exception(response.text)
response_body = response.json()

  # The service account only has access to its one associated
  # deployment, so we get element 0
deployment = response_body.get('data')[0]

deployment_id = deployment['deploymentId']

pprint.pprint(deployment_id)

##############################################################################################
#
#
# get list of username guids here to query for later
#
#
# Set the limit to retrieve more machines and the offset to shift the page
# If you add name to the query params you can query a specific user by name
# ('name': {name})
def get_userguid(username):

    params = {'limit': 1, 'offset': 0, 'deploymentId': deployment_id, 'name': username}

    response = session.get("{}/machines/entitlements/adusers?enabled=true".format(api_url), params=params)

    if not response.status_code == 200:
        raise Exception(response.text)
    response_body = response.json()

    ad_users = response_body.get('data')

    #pprint.pprint("Total Users: {}".format(response_body.get('total')))
    #pprint.pprint(ad_users)

    if ad_users:
        user_guid = ad_users[0]['userGuid']
        return user_guid
    else:
        print('No users!')
    

##############################################################################################

# Set the limit to retrieve more machines and the offset to shift the page
# If you add computerName to the query params you can query a specific
# machine ('computerName': {name})

def getcomputerinfo(machinename):
    params = {'limit': 10000, 'offset': 0, 'deploymentId': deployment_id, 'machineName': machinename}

    response = session.get("{}/machines".format(api_url), params=params)

    """
    The above code is equivalent to
    response = session.get("{}/machine/entitlements/adcomputers?limit=1&offset=0&deploymentId={}".format(api_url, deployment_id))
    """

    if not response.status_code == 200:
        raise Exception(response.text)
    response_body = response.json()

    ad_computers = response_body.get('data')
    #print(ad_computers)
    if ad_computers != []:
        return ad_computers[0]['machineId']

def addmachine(machinename):
    body = dict(
        machineName= machinename,
        deploymentId=deployment_id,
        provider='onprem',
        managed=False,
    )

    response = session.post("{}/machines".format(api_url), json=body)

    if not response.status_code == 201:
        raise Exception(response.text)
    response_body = response.json()
    machine = response_body.get('data')
    #pprint.pprint(machine)

    machine_id = machine['machineId']
    print machine_id
    return machine_id


def setusermachine(machinename,usid):
    body = dict(
        deploymentId=deployment_id,
        machineId=machinename,
        userGuid=usid,
    )

    response = session.post("{}/machines/entitlements".format(api_url),
    json=body)
    if not response.status_code == 201:
        print(response.text)
    response_body = response.json()

    entitlement = response_body.get('data')

with open('./list.csv', 'r') as read_obj:
    csv_reader = DictReader(read_obj)
    for row in csv_reader:
        print(row)
        username = "{} {}".format(row["firstname"],row["lastname"])
        computername = row["machine_name"]
        print("getting userid")
        userguid = get_userguid(username)
        print("getting computerid")
        computerid = getcomputerinfo(computername)
        if computerid == None:
            print("computer id not found adding computer")
            computerid = addmachine(computername)
        print("adding user to computer entitlement")
        setusermachine(computerid,get_userguid(username))

