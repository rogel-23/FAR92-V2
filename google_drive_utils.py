import json
import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from supabase import create_client

def list_rapports_for_arbitre(arbitre_id):
    """
    Liste les rapports PDF associés à un arbitre donné (via son ID) dans le bucket Supabase.
    Retourne une liste de tuples (nom du fichier, URL publique).
    """
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    bucket = "rapports"

    res = supabase.storage.from_(bucket).list(path=arbitre_id)
    if getattr(res, "error", None):
        raise Exception(f"Erreur Supabase (list) : {res.error.message}")

    fichiers = res  # liste d'objets [{'name': ..., 'created_at': ..., ...}]
    urls = []
    for fichier in fichiers:
        path = f"{arbitre_id}/{fichier['name']}"
        url = supabase.storage.from_(bucket).get_public_url(path)
        urls.append((fichier["name"], url))
    
    return urls


SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    import json
    service_account_info = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=credentials)
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


