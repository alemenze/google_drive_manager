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
check_parent='1ozzzqaZ2DZwcr1STk3eKIpX2gV0ekstH'

# Check if File exists
def fileInGDrive(filename, parent):
    results = SERVICE.files().list(q="mimeType='*/*' and name='"+filename+"' and trashed = false and parents in '"+parent+"'",fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if items:
        return True
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

def filesInGDrive(parent):
    results=SERVICE.files().list(q="'"+parent+"' in parents and mimeType='*/*'", fields="nextPageToken, files(id, name, description)").execute()
    items = results.get('files', [])
    return items

def foldersInGDrive(parent):
    results=SERVICE.files().list(q="'"+parent+"' in parents and mimeType='application/vnd.google-apps.folder'", fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    return items

def writeFromGDrive(file_id, file_name, dest, md5):
    request = SERVICE.files().get_media(fileId=file_id)
    fh = io.FileIO(dest+'/'+file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        try:
            status, done = downloader.next_chunk()
        except:
            fh.close()
            os.remove(location + filename)
            print('ERROR downloading file: '+file_name)
        print(f'\rDownload {int(status.progress() * 100)}%.', end='')
    print('\n', flush=True)   
    dest_md5=md5_check.md5_file(os.path.join(dest+'/'+file_name))
    if dest_md5==md5:
        print('md5 checks out.')
    else:
        print('md5 error- something corrupted')

def downloader(download_dirs, downparent_folder=PARENT_FOLDER):
    for item in download_dirs:
        itemG=item[0]
        itemD=item[1]
        if folderInGDrive(itemG, downparent_folder)==False:##This is the second check, since its automated it will always be false after the first one.
            if downparent_folder != check_parent:
                try:
                    os.mkdir(itemD)
                except:
                    pass
                to_download_files=filesInGDrive(downparent_folder)
                for file in to_download_files:
                    writeFromGDrive(file['id'], file['name'],itemD,file['description'])
                to_download_folders=foldersInGDrive(downparent_folder)
                for folder in to_download_folders:
                    downloader([[folder['name'],os.path.join(itemD,folder['name'])]],folder['id'])
            else:
                print('error on your inception folder')

        elif folderInGDrive(itemG, downparent_folder)[0]==True:
            downparent_folder=folderInGDrive(itemG, downparent_folder)[1]##This is the first check.
            try:
                os.mkdir(os.path.join(itemD, itemG))
            except:
                pass
            to_download_files=filesInGDrive(downparent_folder)
            for file in to_download_files:
                writeFromGDrive(file['id'], file['name'],os.path.join(itemD, itemG),file['description'])
            to_download_folders=foldersInGDrive(downparent_folder)
            for folder in to_download_folders:
                downloader([[folder['name'],os.path.join(os.path.join(itemD, itemG),folder['name'])]],folder['id'])
