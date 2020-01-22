from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaFileUpload,MediaIoBaseDownload
import io
import os
import md5_check

# Setup the Drive v3 API
CLIENT_SECRET='./client_secret.json'
SCOPES = 'https://www.googleapis.com/auth/drive.file'
store = file.Storage('./token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('./client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
SERVICE = build('drive', 'v3', http=creds.authorize(Http()))
PARENT_FOLDER='1ozzzqaZ2DZwcr1STk3eKIpX2gV0ekstH'

# Check if File exists
def fileInGDrive(filename, parent):
    results = SERVICE.files().list(q="mimeType='*/*' and name='"+filename+"' and trashed = false and parents in '"+parent+"'",fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    else:
        return False

# Check if Folder exists
def folderInGDrive(filename, parent):
    results = SERVICE.files().list(q="mimeType='application/vnd.google-apps.folder' and name='"+filename+"' and trashed = false and parents in '"+parent+"'",fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if items:
        return True,items[0]['id']
    else:
        return False

# Create Folder
def createGDriveFolder(filename,parent):
    file_metadata = {'name': filename,'parents': [parent],
    'mimeType': "application/vnd.google-apps.folder"}

    folder = SERVICE.files().create(body=file_metadata,
                                        fields='id').execute()
    print('Upload Success!')
    print('FolderID:', folder.get('id'))
    return folder.get('id')

#  Upload files to Google Drive
def writeToGDrive(filename,source,folder_id, md5):
    file_metadata = {'name': filename,
                     'parents': [folder_id],
                     'mimeType': '*/*',
                     'description': md5}
    media = MediaFileUpload(source,
                            chunksize=1024 * 1024,
                            mimetype='*/*',
                            resumable=True)

    if fileInGDrive(filename, folder_id) is False:
        file = SERVICE.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id')
        response = None
        while response is None:
            status, response = file.next_chunk()
            if status:
                print("Uploaded %d%%." % int(status.progress() * 100))
        
        check=fileInGDrive(filename, folder_id)
        print('Upload Success!')
        return check
        
    else:
        print('File already exists as', filename)

def uploader(upload_dirs, upparent_folder=PARENT_FOLDER):
    for item in upload_dirs:
        item_base=item.rstrip('/')
        item=item.rstrip('/').split('/')[-1]
        if folderInGDrive(item, upparent_folder)==False:
            folder_id=createGDriveFolder(item, upparent_folder)
            print('New Folder', item, folder_id)
            new_parent=folder_id
        elif folderInGDrive(item,upparent_folder)[0]==True:
            new_parent=folderInGDrive(item)[1]

        one_dir=[]
        for dirpath, dirnames, filenames in os.walk(item_base, topdown=True):

            #add all directories one level down to list to then loop through next
            if dirpath.count(os.sep) - item_base.count(os.sep) == 1:
                one_dir.append(dirpath)
            #remove all the files that arent in the immediate directory
            if dirpath.count(os.sep) - item_base.count(os.sep) != 0:
                del dirnames[:]
                del filenames[:]
            #take just the remaining files and copy on over
            for f in filenames:
                if fileInGDrive(f, new_parent)==False:
                    source_md5=md5_check.md5_file(os.path.join(dirpath,f))
                    up_id=writeToGDrive(f, os.path.join(dirpath, f), new_parent, source_md5)
                    up_md5 = SERVICE.files().get(fileId=up_id, fields='description').execute()
                    
                    if source_md5 != up_md5['description']:
                        print('ERROR IN UPLOAD')
                    else:
                        print('md5 uploaded correctly')

        #re-loop to next level
        uploader(one_dir, new_parent)

