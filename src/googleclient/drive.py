import os
import io
from datetime import datetime
from time import sleep
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from PIL import Image, ExifTags, ImageOps
from googleclient.client import authenticate
from pathlib import Path

def sync_drive_folder(service, folder_id, local_path):

    os.makedirs(local_path, exist_ok=True)
    
    remote_files = list_drive_files(service, folder_id)
    local_files = list_local_files(local_path)

    # --- Delete any local files missing from Drive ---    
    for name, path in local_files.items():
        if name not in remote_files:
            print(f"[Sync] Deleting local file no longer in Drive: {name}")
            try:
                path.unlink()
            except Exception as e:
                print(f"[Sync] Failed to delete {name}: {e}")

    # --- Download new or missing files ---
    for name, info in remote_files.items():
        dest = local_path / name
        if dest.exists():
            continue  # skip existing files for simplicity; could compare size/time
        
        print(f"[Sync] Downloading new file: {dest}")
        download_file(service, file_id=info['id'], filepath=dest)
       

def list_local_files(path):
    return {p.name: p for p in path.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")}

def list_drive_files(service, folder_id):
    page_token = None
    remote_files = {}

    # --- Get all image files in the folder ---
    while True:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false and mimeType contains 'image/'",
            fields="nextPageToken, files(id, name, modifiedTime, size)",
            pageToken=page_token
        ).execute()

        for f in results.get('files', []):
            remote_files[f['name']] = f  # map name → metadata

        page_token = results.get('nextPageToken')
        if not page_token:
            break
    return remote_files

def download_file(service, file_id, filepath):
    """Download a file from Drive."""
        
    request = service.files().get_media(fileId=file_id)
    with io.FileIO(filepath, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Downloading {filepath}: {int(status.progress() * 100)}%")
   
    return prepare_image(filepath)

def prepare_image(img_path, size=(800, 480)):
    # Open the image
    image = Image.open(img_path)
    # Remove EXIF-based rotation (normalize orientation)
    image = ImageOps.exif_transpose(image)
    # Center-crop and scale to the desired size, preserving aspect ratio
    image = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

    image.save(img_path)
    return img_path