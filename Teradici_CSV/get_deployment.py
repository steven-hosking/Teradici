import requests
import pprint
import yaml


def load_configs(zone):
    conf_path = f'./config/{zone}/conf.yml'
    try:
        with open(conf_path, 'r') as f:
            data = yaml.safe_load(f)
            credentials_data = data['credentials']
            return credentials_data
    except OSError:
        print('cannot open', conf_path)


def deployment(zone):
    credentials = load_configs(zone=zone)

    request_body = dict(username=credentials['auth']['username'],
                        password=credentials['auth']['apiKey'],
                        tenantId=credentials['auth']['tenantId'])

    response = requests.post("{}/auth/signin".format(credentials['api_url']), json=request_body)
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
    response = session.get("{}/deployments".format(credentials['api_url']))

    if not response.status_code == 200:
        raise Exception(response.text)
    response_body = response.json()

    # The service account only has access to its one associated
    # deployment, so we get element 0
    deployment = response_body.get('data')[0]

    deployment_id = deployment['deploymentId']

    pprint.pprint(deployment_id)

    return deployment, session
