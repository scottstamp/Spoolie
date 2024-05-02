import nfc
import nfc.snep
import time

class DefaultSnepServer(nfc.snep.SnepServer):
    def __init__(self, llc):
        nfc.snep.SnepServer.__init__(self, llc, "urn:nfc:sn:snep")

    def process_put_request(self, ndef_message):
        print("client has put an NDEF message")
        for record in ndef_message:
            print(record)
        return nfc.snep.Success

def startup(llc):
    global my_snep_server
    my_snep_server = DefaultSnepServer(llc)
    return llc

def connected(llc):
    my_snep_server.start()
    return True

my_snep_server = None
clf = nfc.ContactlessFrontend("com:COM6:pn532")
clf.connect(llcp={'on-startup': startup, 'on-connect': connected})

while True:
    time.sleep(10)