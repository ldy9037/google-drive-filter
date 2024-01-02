import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]
FILTER = "[bMtMPqp].stop"

def main():
    stack = []

    drives = get_dirves()
    for drive in drives:
        #if drive['name'] == 'GSO':
          stack.append(drive['id'])

          while stack:
            folder_id = stack.pop()
            files = get_files(drive['id'], folder_id)
            for file in files:
              print(f"파일 : {file['name']} ({file['id']})") 

            folders = get_folders(drive['id'], folder_id)
            for folder in folders:
              print(f"폴더 : {folder['name']}")
              stack.append(folder['id'])

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

def get_dirves():
  result = []
  
  try:
    service = build("drive", "v3", credentials=_credentials())

    results = (
        service.drives()
        .list(
            q="name = 'GSO'",
            fields="nextPageToken, drives(id, name)"
        )
        .execute()
    )
    result = results.get("drives", [])

  except HttpError as error:
    print(f"An error occurred: {error}")

  return result

def get_files(drive_id, folder_id):
    result = []

    try:
        service = build("drive", "v3", credentials=_credentials())

        results = (
            service.files()
            .list(
                q="'" + folder_id + "' in parents and trashed=false and name contains '" + FILTER + "'",
                corpora="drive",
                driveId=drive_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                fields="files(id, name)"
            )
            .execute()
        )
        result = results.get("files", [])

    except HttpError as error:
        print(f"An error occurred: {error}")

    return result

def get_folders(drive_id, folder_id):
  result = []

  try:
      service = build("drive", "v3", credentials=_credentials())

      results = (
          service.files()
          .list(
              q="'" + folder_id + "' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false",
              corpora="drive",
              driveId=drive_id,
              includeItemsFromAllDrives=True,
              supportsAllDrives=True,
              fields="files(id, name)"
          )
          .execute()
      )
      result = results.get("files", [])

  except HttpError as error:
      print(f"An error occurred: {error}")

  return result

if __name__ == "__main__":
  main()