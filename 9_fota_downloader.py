#!/usr/bin/env python
__author__ = 'Riccardo Pozza, r.pozza@surrey.ac.uk'

import requests
import json
import argparse
import binascii
import swiftclient
import socket
from retrying import retry

@retry(stop_max_attempt_number=10, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def retryreq(*args, **kwargs):
    r = requests.request(*args, **kwargs)
    parsed = json.loads(r.content)
    return parsed

def getclients(lwm2m_host, lwm2m_port):
    lwm2m_url = "http://" + lwm2m_host + ":" + str(lwm2m_port) + "/api/clients?"
    reply = retryreq('GET',lwm2m_url)
    clients = [str(client['endpoint']) for client in reply]
    return clients

def compute_crc(client, startAddress):
    f = open('./' + client + '.bin', 'rb')
    f.seek(startAddress)
    crc = f.read()
    crc = (binascii.crc32(crc) & 0xFFFFFFFF)
    f.close()
    f = open(client + '.bin.crc', 'w')
    out_str = "crc:%08X" % crc
    f.write(out_str)
    f.close()

def upload_to_swift(swift, container, client, version):
    path = container + "/" + str(version)
    binary = open(client + '.bin', 'r')
    crc = open(client + '.bin.crc', 'r')
    swift.put_object(path, client + '.bin', contents=binary, content_type='text/plain')
    swift.put_object(path, client + '.bin.crc', contents=crc, content_type='text/plain')
    binary.close()
    crc.close()

def start_upgrade(client, lwm2m_host, lwm2m_port, fota_host, fota_port, fota_path, version):
    lwm2m_url = "http://" + lwm2m_host + ":" + str(lwm2m_port) + "/api/clients/" + client + "/5/0/1"
    fota_host_resolved = socket.gethostbyname(fota_host)
    fota_url = "http://" + fota_host_resolved + ":" + str(fota_port) + fota_path + "/" + version + "/"
    header_json = {'Content-Type': 'application/json'}
    payload_now = {'id': 1, 'value': fota_url}
    reply = retryreq('PUT', lwm2m_url,headers=header_json, json=payload_now)
    lwm2m_url = lwm2m_url[:-1] + str(2)
    r = requests.post(lwm2m_url)
    print r

def main():
    with open('lwm2mconfig.json') as config_file:
        config_data = json.load(config_file)

    lwm2m_host = config_data["LWM2MAPIServer"]
    lwm2m_port = config_data["LWM2MAPIPort"]

    swift_host = config_data["SwiftServer"]
    swift_port = config_data["SwiftPort"]
    swift_path = config_data["SwiftPath"]
    swift_container = swift_path.split('/')[3]

    # Setting Swift options
    swift_url = 'http://' + config_data["TestbedController"] + ':5000/v2.0/'
    swift_ver = 2
    swift_user = config_data["TestbedUsername"]
    swift_pass = config_data["TestbedPassword"]
    swift_tena = config_data["TestbedTenantname"]
    swift = swiftclient.Connection(authurl=swift_url, user=swift_user,
                                   key=swift_pass, tenant_name=swift_tena,
                                   auth_version=swift_ver)
    resp_headers, containers = swift.get_account()
    # Check if present or create a new container
    if not containers:
        # create container for dump data
        swift.put_container(swift_container)
    else:
        # check it exists
        found = 0
        for container in containers:
            if container['name'] == swift_container:
                found = 1
        # create if doesn't
        if not found:
            swift.put_container(swift_container)

    # Define and parse command line arguments
    parser = argparse.ArgumentParser(description="FOTA Downloader LWM2M")
    parser.add_argument("-c", "--client", help="endpoint to download (default 'MyClientName00X', for all type 'ALL'")
    parser.add_argument("-v", "--version", help="version to download (default 'v1.0.0')")
    parser.add_argument("-u", "--upload", help="upload binaries to download (default '0')")
    parser.add_argument("-p", "--upgrade", help="upgrade software on client (default '0')")

    # If the log file is specified on the command line then override the default
    args = parser.parse_args()
    clients = []
    upload = int(0)
    version = 'v1.0.0'
    upgrade = int(0)
    if args.upgrade:
        upgrade = int(args.upgrade)
    if args.version:
        version = args.version
    if args.upload:
        upload = int(args.upload)
    if args.client:
        clients.append(args.client)
    if args.client == 'ALL':
        clients = getclients(lwm2m_host, lwm2m_port)

    for client in clients:
        if upload == 1:
            print ">Uploading "
            compute_crc(client,65536)
            upload_to_swift(swift,swift_container,client, version)
        if upgrade == 1:
            print ">Upgrading "
            start_upgrade(client,lwm2m_host, lwm2m_port, swift_host, swift_port, swift_path, version)

if __name__ == '__main__':
    main()
