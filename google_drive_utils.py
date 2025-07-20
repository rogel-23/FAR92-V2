import json
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    if "SERVICE_ACCOUNT_JSON" in st.secrets:
        # ✅ MODE CLOUD (depuis Streamlit secrets)
        service_account_info = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )
    else:
        # ✅ MODE LOCAL (depuis fichier)
        SERVICE_ACCOUNT_FILE = 'service_account.json'
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

    service = build('drive', 'v3', credentials=credentials)
    return service


def upload_to_drive(filepath, filename, parent_folder_id):
    service = get_drive_service()

    file_metadata = {
        'name': filename,
        'parents': [parent_folder_id],  # <- dossier Drive ciblé
    }
    media = MediaFileUpload(filepath, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # Rendre le fichier public
    service.permissions().create(
        fileId=file.get("id"),
        body={"role": "reader", "type": "anyone"},
    ).execute()

    file_url = f"https://drive.google.com/file/d/{file.get('id')}/view?usp=sharing"
    return file_url


