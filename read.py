import nfc
from nfc.clf import RemoteTarget
import ndef
import urllib.request, json
import time

spools = []

def load_json(uri):
    with urllib.request.urlopen(uri) as url:
        return json.load(url)
    
def get_all_spools():
    return load_json('http://192.168.2.99:7912/api/v1/spool?allow_archived=false&limit=200&offset=0&sort=id:asc')

def get_active_spool():
    return load_json('http://192.168.2.160/server/spoolman/spool_id')["result"]["spool_id"]

def set_active_spool(id):
    return

def get_spool_by_id(id):
    return next(spool for spool in spools if (spool["id"] == id))

def get_spool_friendly(spool):
    return "%d. %s %s %s" % (spool["id"], spool["filament"]["vendor"]["name"], spool["filament"]["material"], spool["filament"]["name"])

def get_spool_url(spool):
    return "http://192.168.2.99:7912/spool/show/%d" % spool["id"]

active_spool_id = get_active_spool()
spools = get_all_spools()

print("Active spool from [Ender] is", get_spool_friendly(get_spool_by_id(active_spool_id)), "\n")


clf = nfc.ContactlessFrontend('com:COM6:pn532')
while True:
    tag = clf.connect(rdwr={'on-connect': lambda tag: False})

    if tag.ndef is None:
        print('presented tag is not programmed as a spool tag, retrying...')
        time.sleep(5)
        continue
    
    scanned_spool = {}
    for record in tag.ndef.records:
        if record.type == ndef.TextRecord._type:
            # print(record.name, str(record.text))
            if record.name == 'ID':
                scanned_spool = get_spool_by_id(int(record.text))
        # elif record.type == ndef.UriRecord._type:
            # print(record.name, str(record.uri))

    if scanned_spool:
        if scanned_spool["id"] != active_spool_id:
            

        print('found valid spool tag: ', get_spool_friendly(scanned_spool), get_spool_url(scanned_spool))
    else:
        print('found N2xx tag, please program this tag before use')
    
    time.sleep(5)