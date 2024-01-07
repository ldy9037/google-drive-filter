import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]
FILTER = "Test"

def delete_encrypted_version():
  drives = get_drives()
  
  page_token = None
  for drive in drives:
    if drive['name'] == "Test-drive":
      while True:
        files = get_files(drive['id'], page_token)
        page_token = files['nextPageToken']
          
        for file in files['files']:
            print(f"{file['name']}")
      
            revisions = get_revisions(file['id'])    
            for revision in revisions['revisions']:
                print(f"{revision['id']} : {revision['modifiedTime']}")
            
            if len(revisions['revisions']) >= 2:
                print("ttt")
                delete_revision(file['id'], revisions['revisions'][-1]['id'])
                
        if not page_token:
            break

def restore():
  drives = get_drives()
  
  page_token = None
  for drive in drives:
    while True:    
      files = get_deleted_files(drive['id'], page_token)
      page_token = files['nextPageToken']    
        
      for file in files['files']:
          print(f"{file['name']}")
          restore_files(drive['id'], file['id'])
          
      if not page_token:
          break
          
def delete():
  drives = get_drives()
  
  page_token = None
  for drive in drives:
    if drive['name'] == "N/W 인프라 개선사업":
      while True:    
        files = get_files(drive['id'], page_token)
        page_token = files['nextPageToken']  
          
        for file in files['files']:
            print(f"{file['name']}")
            deleted_file = delete_files(drive['id'], file['id'])
        
        if not page_token:
            break
        
def _credentials():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  
  return creds

def get_drives():
  result = []
  
  try:
    service = build("drive", "v3", credentials=_credentials())

    results = (
        service.drives()
        .list(
            fields="nextPageToken, drives(id, name)"
        )
        .execute()
    )
    result = results.get("drives", [])

  except HttpError as error:
    print(f"An error occurred: {error}")

  return result

def restore_files(drive_id ,file_id):
  try:
      service = build("drive", "v3", credentials=_credentials())

      results = (
          service.files()
          .update(
              fileId=file_id,
              supportsAllDrives=True,
              body={
                'trashed' : False
              }
          )
          .execute()
      )

  except HttpError as error:
      print(f"An error occurred: {error}")

def delete_files(drive_id ,file_id):
  try:
      service = build("drive", "v3", credentials=_credentials())

      results = (
          service.files()
          .update(
              fileId=file_id,
              supportsAllDrives=True,
              body={
                'trashed' : True
              }
          )
          .execute()
      )

  except HttpError as error:
      print(f"An error occurred: {error}")

def get_files(drive_id, page_token):
    result = {
      'files' : [],
      'nextPageToken' : None
    }

    try:
        service = build("drive", "v3", credentials=_credentials())

        results = (
            service.files()
            .list(
                q="trashed=false and name contains '" + FILTER + "'",
                corpora="drive",
                pageSize=1000,
                driveId=drive_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                pageToken=page_token,
                fields="nextPageToken, files(id, name)"
            )
            .execute()
        )
        result['files'] = results.get("files", [])
        result['nextPageToken'] = results.get("nextPageToken")
    except HttpError as error:
        print(f"An error occurred: {error}")

    return result

def get_deleted_files(drive_id, pageToken):
  result = {
    'files' : [],
    'nextPageToken' : None
  }

  try:
      service = build("drive", "v3", credentials=_credentials())

      results = (
          service.files()
          .list(
              q="trashed=true",
              corpora="drive",
              pageSize=1000,
              driveId=drive_id,
              includeItemsFromAllDrives=True,
              supportsAllDrives=True,
              pageToken=pageToken,
              fields="nextPageToken, files(id, name)"
          )
          .execute()
      )
      result['files'] = results.get("files", [])
      result['nextPageToken'] = results.get("nextPageToken", None)

  except HttpError as error:
      print(f"An error occurred: {error}")

  return result

def get_revisions(file_id):
    result = {
      'revisions' : []
    }

    try:
        service = build("drive", "v3", credentials=_credentials())

        results = (
            service.revisions()
            .list(
                fileId=file_id,
                fields="revisions(id, modifiedTime)"
            )
            .execute()
        )
        print(results)
        result['revisions'] = results.get("revisions", [])
        
    except HttpError as error:
        print(f"An error occurred: {error}")

    return result

def delete_revision(file_id, revision_id):
    try:
        service = build("drive", "v3", credentials=_credentials())

        results = (
            service.revisions()
            .delete(
                fileId=file_id,
                revisionId=revision_id
            )
            .execute()
        )
        
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
  delete_encrypted_version()