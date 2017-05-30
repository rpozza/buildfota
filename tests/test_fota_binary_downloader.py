#!/usr/bin/env python
__author__ = 'Riccardo Pozza, r.pozza@surrey.ac.uk'

import requests
import binascii
import time
import sys
import json
import argparse

# definition of variables TODO optparser
with open('testconfig.json') as config_file:
        config_data = json.load(config_file)

hostname = config_data["LWM2MAPIServer"]
port = config_data["LWM2MAPIPort"]
max_number_attemps = 5

# objects definition
firmware = 5

# instance definition
instance_number = 0  # all use cases just one instance

# resources definition
fwpackage = 0
fwuri = 1
fwstate = 3
fwresult = 5


def main():
    # Define and parse command line arguments
    parser = argparse.ArgumentParser(description="FOTA Downloader LWM2M")
    parser.add_argument("-c", "--client", help="endpoint to download (default 'MyClientName00X', for all type 'ALL'")

    # If the log file is specified on the command line then override the default
    args = parser.parse_args()
    fullclientlist = []
    if args.client:
        fullclientlist.append(args.client)
    if args.client == 'ALL':
        fullclientlist = getclientlist(hostname, port)

    #TODO: provide different options and stop observations before downloading
    for cname in fullclientlist:
        fhand = openbinaryhandlers(cname)

        #illuminance
        while True:
            response = cancelobservation(hostname, port, cname, 3301)
            if response == True:
                break

            time.sleep(2)
        #temperature
        while True:
            response = cancelobservation(hostname, port, cname, 3303)
            if response == True:
                break

            time.sleep(2)
        #humidity
        while True:
            response = cancelobservation(hostname, port, cname, 3304)
            if response == True:
                break

            time.sleep(2)
        #loudness
        while True:
            response = cancelobservation(hostname, port, cname, 3324)
            if response == True:
                break

            time.sleep(2)
        #concentration
        while True:
            response = cancelobservation(hostname, port, cname, 3325)
            if response == True:
                break

            time.sleep(2)
        #distance
        while True:
            response = cancelobservation(hostname, port, cname, 3330)
            if response == True:
                break

            time.sleep(2)
        #multistate
        while True:
            response = cancelobservation(hostname, port, cname, 3348)
            if response == True:
                break

            time.sleep(2)

        #0: wait for the client to be ready
        while True:
            response, value = getvalue(hostname, port, cname, fwresult)
            if response == requests.codes.ok:
                if value == 1:
                    # erased
                    print "Client " + str(cname) + " Ready!"
                    break

            time.sleep(2)

        #1: erase flash memory (send "start" command)
        sys.stdout.write("Now, Erasing Flash Memory...")
        sys.stdout.flush()
        response = putvaluejson(hostname, port, cname, fwuri, "start")
        if response != requests.codes.ok:
            print "Failed HTTP response code: " + str(response)
            raise SystemExit
        #2: wait external flash memory erased
        while True:
            response, value = getvalue(hostname, port, cname, fwresult)
            if response == requests.codes.ok:
                if value == 1:
                    #erased
                    print "Erased!"
                    break

            time.sleep(2)

        print "Now, Downloading Firmware!"
        page_number = 0
        page = get_page(fhand)

        while True:
            # 3: read a 256 byte page from external file (each of 512 bytes is a char 0-9-A-F)
            if len(page) == 0:
                #no more bytes to program
                print "Reached End of File!"
                #adjusting number of pages sent
                page_number += 1
                break

            if len(page) < 512:
                # pad last page
                print "Padding Last Page!"
                pads = 512 - len(page)
                for i in range(pads):
                    page += "0"

            sys.stdout.write("Sending Page " + str(page_number) + "...")
            sys.stdout.flush()
            # 4: prepare the address+page packet and send it OTA
            downpage = '{:08x}'.format((page_number*256),'X') + page
            while True:
                response = putvaluejson(hostname, port, cname, fwpackage, downpage)
                if response == requests.codes.ok:
                    print "Page " + str(page_number) + " Sent!"
                    break
                # give some time for recovery from registration fails, connectivity
                time.sleep(5)
                print "Failed"
                sys.stdout.write("Retrying Page " + str(page_number) + "...")
                sys.stdout.flush()

            # 5: wait for the page to be actually written to the external flash
            while True:
                response, value = getvalue(hostname, port, cname, fwresult)
                if response == requests.codes.ok:
                    if value == 1:
                        # erased
                        print "Page " + str(page_number) + " Written to Flash!"
                        break

                time.sleep(2)

            # 6: retrieve the page just written to the external flash
            sys.stdout.write("Reading Page " + str(page_number) + "...")
            sys.stdout.flush()
            while True:
                response, packet = getvalue(hostname, port, cname, fwpackage)
                if response == requests.codes.ok:
                    break

                time.sleep(2)

            externalflashpage = ''.join(packet).upper()

            if page == externalflashpage:
                print "Check OK!!"
                print externalflashpage
                page_number +=1
                page = get_page(fhand)
            else:
                print "Check NOT OK!! Retrying!"

        # 7: program the firmware stop address to the external flash
        print "Firmware Downloaded! Writing Stop Address!"
        response = putvaluejson(hostname, port, cname, fwuri, "stop")
        if response != requests.codes.ok:
            print "Failed HTTP response code: " + str(response)
            raise SystemExit
        # 8: wait for the firmware stop address to be written
        while True:
            response, value = getvalue(hostname, port, cname, fwresult)
            if response == requests.codes.ok:
                if value == 1:
                    # erased
                    print "Stop Address written!"
                    break

            time.sleep(2)

        # 9: check if the state is downloaded
        while True:
            response, value = getvalue(hostname, port, cname, fwstate)
            if response == requests.codes.ok:
                if value == 2:
                    # erased
                    print "Ready for Finalization!"
                    break

            time.sleep(2)

        # 10: retrieve the final software version downloaded
        while True:
            response, packet = getvalue(hostname, port, cname, fwpackage)
            if response == requests.codes.ok:
                break

            time.sleep(2)

        print "Stop Address is " + binascii.unhexlify(''.join(packet).upper()) + " !"

        # 11: program the firmware id to the external flash
        print "Firmware Downloaded! Writing Magic Number!"
        response = putvaluejson(hostname, port, cname, fwuri, "checked")
        if response != requests.codes.ok:
            print "Failed HTTP response code: " + str(response)
            raise SystemExit
        # 12: wait for the version ID to be written
        while True:
            response, value = getvalue(hostname, port, cname, fwresult)
            if response == requests.codes.ok:
                if value == 1:
                    # erased
                    print "Magic Number written!"
                    break

            time.sleep(2)

        # 13: check if the state is downloaded
        while True:
            response, value = getvalue(hostname, port, cname, fwstate)
            if response == requests.codes.ok:
                if value == 3:
                    # erased
                    print "Ready for Update!"
                    break

            time.sleep(2)

        # 14: retrieve the final software version downloaded
        while True:
            response, packet = getvalue(hostname, port, cname, fwpackage)
            if response == requests.codes.ok:
                break

            time.sleep(2)

        print "New Software " + binascii.unhexlify(''.join(packet).upper()) + " Has Been Downloaded to External Flash!"
        closebinaryhandlers(fhand)

        #reboot
        print "Safely Rebooting! Attempting a few times to be sure!"
        postvalue(hostname, port, cname, 2)



def getclientlist(fqdn, port):
    attempts = 0
    clientslist = []
    fullurl = "http://" + fqdn + ":" + str(port) + "/api/clients?"
    while attempts < max_number_attemps:
        r = requests.get(fullurl)
        attempts += 1
        if r.status_code == requests.codes.ok:
            for clients in r.json():
                clientslist.append(str(clients['endpoint']))
            return clientslist
    print "Error! cannot retrieve clients list!"
    raise SystemExit

def openbinaryhandlers(client):
    f = open(client + ".bin", 'rb')
    return f

def closebinaryhandlers(fileh):
    fileh.close()

def getvalue(fqdn, port, client, resource):
    attempts = 0
    objecturl = "/" + str(firmware) + "/" + str(instance_number) + "/" + str(resource)
    fullurl = "http://" + fqdn + ":" + str(port) + "/api/clients/" + client + objecturl
    while attempts < max_number_attemps:
        r = requests.get(fullurl)
        attempts += 1
        if r.status_code == requests.codes.ok:
            value = r.json()['content']['value']
            return r.status_code,value

        time.sleep(attempts * 0.2)

    print "Maximum Number of Attempts achieved!"
    return r.status_code,-1

def putvaluejson(fqdn, port, client, resource, datavalue):
    header_json = {'Content-Type': 'application/json'}
    payload_now = {'id': resource, 'value': datavalue}
    objecturl = "/" + str(firmware) + "/" + str(instance_number) + "/" + str(resource) # time
    fullurl = "http://" + fqdn + ":" + str(port) + "/api/clients/" + client + objecturl
    attempts = 0
    while attempts < max_number_attemps:
        r = requests.put(fullurl,headers=header_json, json=payload_now)
        attempts += 1
        if r.status_code == requests.codes.ok:
            return r.status_code
        time.sleep(attempts * 0.2)

    print "Maximum Number of Attempts achieved!"
    return r.status_code

def deletevalue(fqdn, port, client, object, resource):
    attempts = 0
    objecturl = "/" + str(object) + "/" + str(instance_number) + "/" + str(resource)
    fullurl = "http://" + fqdn + ":" + str(port) + "/api/clients/" + client + objecturl + "/observe"
    while attempts < max_number_attemps:
        r = requests.delete(fullurl)
        attempts += 1
        if r.status_code == requests.codes.ok:
            return True

        time.sleep(attempts * 0.2)

    print "Maximum Number of Attempts achieved!"
    return False

def cancelobservation(fqdn, port, client, object):
    attempts = 0
    objecturl = "/" + str(object) + "/" + str(instance_number)
    fullurl = "http://" + fqdn + ":" + str(port) + "/api/clients/" + client + objecturl + "/observe"
    while attempts < max_number_attemps:
        r = requests.delete(fullurl)
        attempts += 1
        if r.status_code == requests.codes.ok:
            return True

        time.sleep(attempts * 0.2)

    print "Maximum Number of Attempts achieved!"
    return False

def postvalue(fqdn, port, client, resource):
    attempts = 0
    objecturl = "/" + str(firmware) + "/" + str(instance_number) + "/" + str(resource)
    fullurl = "http://" + fqdn + ":" + str(port) + "/api/clients/" + client + objecturl
    while attempts < max_number_attemps:
        r = requests.post(fullurl)
        attempts += 1
        if r.status_code == requests.codes.ok:
            return True

        time.sleep(attempts * 0.2)

    print "Maximum Number of Attempts achieved!"
    return False

def get_page(fileh):
    bytes = fileh.read(256)
    packet = binascii.hexlify(bytes).upper()
    return packet

if __name__ == '__main__':
    main()
