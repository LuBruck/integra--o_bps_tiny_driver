import pickle
import json
import os
from datetime import datetime
from loguru import logger
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload, MediaIoBaseDownload

API_URL = ['https://www.googleapis.com/auth/drive']

class Drive():

    def __init__(self):
        creds = None

        # Checks if authentication token exists, then load it
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # Create new authencation token if it does not exist or has expired
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', API_URL)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.__service = build('drive', 'v3', credentials=creds)

    # List all files inside specified Drive folder
    def list_files(self, folder_id):
        # Call API
        response = self.__service.files().list(
            q=f"'{folder_id}' in parents", fields='files(id,name,modifiedTime,mimeType)'
        ).execute()

        # Return all file names
        files_dict = {"all": response.get('files', []), "names": []}
        for item in files_dict['all']:
            files_dict['names'].append(item['name'])

        return files_dict

        # Upload file from local to drive folder
    def upload_file(self, filename, local_path, folder_id, update=False):
        local_absolute_path = f"{local_path}/{filename}"

        date_now = datetime.now()
        file_metadata = {
            'name': filename,
            'modifiedTime': date_now.isoformat("T") + "Z",
            'parents': [folder_id]
        }

        # File definitions for upload
        media = MediaFileUpload(local_absolute_path)

        # Send POST request for upload API
        try:
            if update != False:
                uploaded_file = self.__service.files().update(fileId =update, media_body=media).execute()

                logger.info("Remote file '{}' updated successfully in folder '{}'.", filename, local_absolute_path)

            else:
                # print('ta ak')
                uploaded_file = self.__service.files().create(
                    body=file_metadata, media_body=media, fields='id'
                ).execute()

                logger.info("File '{}' uploaded successfully in folder '{}'.", filename, local_absolute_path)

            return uploaded_file
        except Exception as erro:
            logger.error("Error uploading file: {}.", filename)
            print(erro)

            return False
    

class main():
    configs = json.load(open("utils/api_google_driver/configs.json", "r", encoding='utf-8'))

    def __init__(self):
        # Make sure configuration file exists and is updated
        # if not os.path.exists("./configs.json"):
            # logger.error(
            #     "Please rename example file 'configs-example.json' to 'configs.json' and update all required fields."
            # )
            # return
        configs = self.configs

        # Make sure backup folder exists
        if not os.path.exists(configs["local_folder_path"]):
            logger.error("Create backup folder on '{}'.", configs["local_folder_path"])
            return

        # Configure logging to file if enabled
        if configs["log_file_path"]:
            log_path = os.path.join(configs["local_folder_path"], "sync.log")
            if not os.path.exists(log_path):
                log_obj = open(log_path, "w")
            else:
                log_obj = open(log_path, "a")

            logger.add(log_obj, format="{time} | {level} | {function} | {message}")
        
    def list_files_driver(self):
        my_drive = Drive()
        lista = my_drive.list_files(self.configs['drive_folder_id'])
        return lista

    def upload_file_driver(self, file_name ,update=False):
        my_drive = Drive()
        lista = self.list_files_driver()['all']
        for arquivo in lista:
            if file_name == arquivo['name'] :
                update = arquivo['id']

        file_updloaded = my_drive.upload_file(file_name, \
            self.configs['local_folder_path'], \
            self.configs['drive_folder_id'], update)

if __name__ == '__main__':
    main = main()
    lista = main.list_files_driver()

    print(lista)
    