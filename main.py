import nfc
from nfc.clf import RemoteTarget
import ndef
import urllib.request, json

spools = []

def load_json(uri):
    with urllib.request.urlopen(uri) as url:
        return json.load(url)

def get_spool_by_id(id):
    return next(spool for spool in spools if (spool["id"] == id))

def get_spool_friendly(spool):
    return "%d. %s %s %s" % (spool["id"], spool["filament"]["vendor"]["name"], spool["filament"]["material"], spool["filament"]["name"])

def get_spool_url(spool):
    return "http://192.168.2.99:7912/spool/show/%d" % spool["id"]

active_spool_id = load_json('http://192.168.2.160/server/spoolman/spool_id')["result"]["spool_id"]

spools = load_json('http://192.168.2.99:7912/api/v1/spool?allow_archived=false&limit=200&offset=0&sort=id:asc')
# with urllib.request.urlopen('http://192.168.2.99:7912/api/v1/spool?allow_archived=false&limit=20&offset=0&sort=id:asc') as url:
    # spools = json.load(url)

print("Active spool from [Ender] is", get_spool_friendly(get_spool_by_id(active_spool_id)), "\n")


for spool in spools:
    print(get_spool_friendly(spool))

selected_id = int(input("\nPlease pick a filament to program to the tag: "))
selected_spool = get_spool_by_id(selected_id)
print("\nYou have selected", get_spool_friendly(selected_spool), "please place the tag near the reader")

clf = nfc.ContactlessFrontend('com:COM6:pn532')
tag = clf.connect(rdwr={'on-connect': lambda tag: False})

# assert tag.ndef is not None
# for record in tag.ndef.records:
#     print(record)
print("\nFound tag, writing, please wait...")

# uri, title = 'http://192.168.2.99:7912/spool/show/1', 'Spool 1'
# tag.ndef.records = [ndef.SmartposterRecord(uri, title)]
record1 = ndef.TextRecord(str(selected_spool["id"]), "en")
record1.name = "ID"
record2 = ndef.UriRecord(get_spool_url(selected_spool))
record2.name = get_spool_friendly(selected_spool);
# record3 = ndef.TextRecord(get_spool_friendly(selected_spool), "en")
# record3.name = "Friendly Name"

tag.ndef.records = [record1, record2]
assert tag.ndef.has_changed is False

print('\nTag written, verifying...')
tag = clf.connect(rdwr={'on-connect': lambda tag: False})

assert tag.ndef is not None
for record in tag.ndef.records:
    print(record)

assert tag.ndef.records[0].text == str(selected_spool["id"])
print('\nTag programmed successfully!')
clf.close()