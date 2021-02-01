import argparse
import get_deployment
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


def get_user_entitlement(user_guids, session, credentials):
    if len(user_guids) > 0:
        tmp_guids = ', '.join(user_guids)
        guids = tmp_guids.replace(' ','')
        params = {'limit': 100, 'offset': 0, 'userGuid': guids}
        response = session.get("{}/machines/entitlements/adusers".format(credentials['api_url']), params=params)

        if not response.status_code == 200:
            raise Exception(response.text)
        response_body = response.json()['data']
        try:
            # user_name = (response_body[0]['userName'])
            user_names = [x['userName'] for x in response_body]
            if len(user_names) > 0:
                return user_names
            else:
                user_names = ["no_user"]
                return user_names

        except:
            user_names = ["no_user"]
            return user_names

    else:
        user_names = ["no_user"]
        return user_names


def get_entitlement(machine_id, session, credentials):
    params = {'limit': 100, 'offset': 0, 'machineId': machine_id}
    response = session.get("{}/machines/entitlements".format(credentials['api_url']), params=params)

    if not response.status_code == 200:
        raise Exception(response.text)
    response_body = response.json()['data']

    try:
        user_guids = [x['userGuid'] for x in response_body]
        user_name = get_user_entitlement(user_guids=user_guids, session=session, credentials=credentials)
    except:
        user_name = ["no_user"]

    return user_name


def get_machines(deployment_data, session, credentials):
    params = {'limit': 10000, 'offset': 0, 'deploymentId': deployment_data['deploymentId']}

    response = session.get("{}/machines".format(credentials['api_url']), params=params)

    if not response.status_code == 200:
        raise Exception(response.text)
    response_body = response.json()['data']

    machine_list = [(x['machineName'], x['machineId']) for x in response_body]
    print(machine_list)
    return machine_list


def get_username(user_guid, session, credentials):
    params = {'limit': 100, 'offset': 0, 'userGuid': user_guid}
    response = session.get("{}/auth/users".format(credentials['api_url']), params=params)
    if not response.status_code == 200:
        raise Exception(response.text)
    response_body = response.json()['data']

    print(response_body)


def create_csv(zone):
    deployment_data, session = get_deployment.deployment(zone=zone)
    credentials = load_configs(zone=zone)
    machine_list = get_machines(deployment_data=deployment_data, session=session, credentials=credentials)
    print("Creating csv...")
    tmp_csv = open(f'./teradici_machine_maps_{zone}.csv', 'w')
    tmp_csv.write('hostname,username\n')
    for machine in machine_list:
        machine_id = machine[1]
        hostname = machine[0]
        tmp_usernames = get_entitlement(machine_id=machine_id, credentials=credentials, session=session)

        if len(tmp_usernames) > 1:
            usernames = ' - '.join(tmp_usernames)

        else:
            usernames = tmp_usernames[0]

        print(f'{hostname}:{usernames}')

        tmp_csv.write('{},{}\n'.format(hostname,usernames))

    tmp_csv.close()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zone', required=True, help='van or syd')
    args = parser.parse_args()
    main(args)


def main(args):
    create_csv(zone=args.zone)


if __name__ == '__main__':
    parse_arguments()
