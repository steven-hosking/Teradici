to_the_cloud.py

Python script to push user to machine mappings for teradici cloud

from_the_cloud.py

For the specified zone, generates a csv file of machines and their assigned users from Teradici Cloud Access Manager

Arguments:
zone:

van
syd
Usage:
python from_the_cloud.py --zone van

python from_the_cloud.py --zone syd

Configuration
Set API url and authentication details under

./config/{ZONE}/conf.yaml

Author: Steven Hosking
