import dropbox
import json
with open('parameters.json') as f:
    parameters = json.load(f)

class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, file_from, file_to):
        """upload a file to Dropbox using API v2
        """
        dbx = dropbox.Dropbox(self.access_token)

        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)

def upload(file_from,file_to):
    access_token = parameters['dropboxToken']
    transferData = TransferData(access_token)

    # API v2
    transferData.upload_file(file_from, file_to)
    print('uploaded '+file_from)
