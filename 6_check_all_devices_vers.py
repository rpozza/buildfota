#!/usr/bin/env python
__author__ = 'Riccardo Pozza, r.pozza@surrey.ac.uk'

import sys
import requests
import json
from retrying import retry

if len(sys.argv) !=2:
    print "Usage: " + sys.argv[0] + " myclient_name"
    sys.exit()

clientprefix = sys.argv[1]

@retry(stop_max_attempt_number=10, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def retryreq(url):
    r = requests.get(url)
    parsed = json.loads(r.content)
    return parsed

with open('lwm2mconfig.json') as config_file:
    config_data = json.load(config_file)

hostname = str(config_data["LWM2MAPIServer"])
port = str(config_data["LWM2MAPIPort"])
baseurl = 'http://' + hostname + ':' + port + '/api/clients'

reply = retryreq(baseurl)

deployed_eggs = set()
for i in range(116):
    deployed_eggs.add(clientprefix+format(i+1, "03d"))

deployed_eggs.remove(clientprefix+ "006")
deployed_eggs.remove(clientprefix+ "007")
deployed_eggs.remove(clientprefix+ "008")
deployed_eggs.remove(clientprefix+ "021")
deployed_eggs.remove(clientprefix+ "032")
deployed_eggs.remove(clientprefix+ "033")
deployed_eggs.remove(clientprefix+ "034")
deployed_eggs.remove(clientprefix+ "035")
deployed_eggs.remove(clientprefix+ "036")
deployed_eggs.remove(clientprefix+ "038")
deployed_eggs.remove(clientprefix+ "039")
deployed_eggs.remove(clientprefix+ "043")
deployed_eggs.remove(clientprefix+ "052")
deployed_eggs.remove(clientprefix+ "060")
deployed_eggs.remove(clientprefix+ "062")
deployed_eggs.remove(clientprefix+ "114")

eggs = set()
for i in range(len(reply)):
    eggs.add(reply[i]['endpoint'])

print "Found " + str(len(eggs)) + " eggs"

regtimes = {}
i = 0
for egg in sorted(eggs):
    i += 1
    reply1 = retryreq(baseurl + '/' + egg)
    regtimes[egg] = reply1['registrationDate']
    reply2 = retryreq(baseurl + '/' + egg + '/5/0')
    print format(i, "03d") + " - Egg: " + str(egg) + ", vers: " + str(reply2['content']['resources'][3]['value'])

i = 0
for times in sorted(regtimes.items(), key=lambda regtimes: regtimes[1]):
    i += 1
    print format(i, "03d") + " - Egg: " + str(times[0]) + ", registered at: " + str(times[1])

remaining_eggs = deployed_eggs - eggs
print "Missing Eggs:" + str(sorted(remaining_eggs))
