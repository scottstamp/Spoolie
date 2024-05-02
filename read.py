import nfc
import ndef
from urllib import request
import json
import time

spools = []


def load_json(uri):
    with request.urlopen(uri) as url:
        return json.load(url)


def post_data(url, data, headers=None):
    """
    POST data string to `url`, return page and headers
    """
    if headers is None:
        headers = {'Content-Type': 'application/json'}

    # if data is not in bytes, convert to it to utf-8 bytes
    bindata = data if type(data) == bytes else data.encode('utf-8')
    # need Request to pass headers
    req = request.Request(url, bindata, headers)
    resp = request.urlopen(req)
    return resp.read(), resp.getheaders()


def send_gcode(command):
    post_data('http://192.168.2.160/api/printer/command',
              json.dumps({'commands': [command]}))


def beep():
    send_gcode('BEEP')


def get_all_spools():
    return load_json('http://192.168.2.99:7912/api/v1/spool?allow_archived=false&limit=200&offset=0&sort=id:asc')


def get_active_spool_id():
    return load_json('http://192.168.2.160/server/spoolman/spool_id')["result"]["spool_id"]


def set_active_spool(id):
    post_data('http://192.168.2.160/server/spoolman/spool_id',
              json.dumps({'spool_id': int(id)}))


def get_spool_by_id(id):
    return next(spool for spool in spools if (spool["id"] == id))


def get_spool_friendly(spool):
    return "%d. %s %s %s" % (spool["id"], spool["filament"]["vendor"]["name"], spool["filament"]["material"], spool["filament"]["name"])


def get_spool_url(spool):
    return "http://192.168.2.99:7912/spool/show/%d" % spool["id"]


active_spool_id = get_active_spool_id()
spools = get_all_spools()

print("Active spool from [Ender] is", get_spool_friendly(
    get_spool_by_id(active_spool_id)), "\n")


clf = nfc.ContactlessFrontend('com:COM6:pn532')
while True:
    tag = clf.connect(rdwr={'on-connect': lambda tag: False})

    if tag.ndef is None:
        print('presented tag is not programmed as a spool tag, retrying...')
        time.sleep(5)
        continue

    scanned_spool = {}
    for record in tag.ndef.records:
        if record.type == ndef.TextRecord._type and record.name == 'ID':
            scanned_spool = get_spool_by_id(int(record.text))

    if scanned_spool:
        print('found valid spool tag: ', get_spool_friendly(
            scanned_spool), get_spool_url(scanned_spool))

        active_spool_id = get_active_spool_id()
        if scanned_spool["id"] != active_spool_id:
            print('scanned spool doesn\'t match active spool, updating!')
            set_active_spool(scanned_spool["id"])
            beep()
            active_spool_id = get_active_spool_id()
        else:
            time.sleep(15)
            continue

    else:
        print('found N2xx tag, please program this tag before use')

    time.sleep(5)
