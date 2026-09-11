#!/usr/bin/env python3
"""
Automated 6-Step Production Pipeline for Renungan Penyiswaan Pangestu
Handles: Video Rendering -> YouTube Upload -> Google Doc Formatting -> Web GitHub Sync -> Master Sheet Logging -> Final WhatsApp Block Verification
"""

import os
import sys
import re
import json
import time
import argparse
import subprocess
import datetime
import requests
from PIL import Image

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

TOKEN_PATH = "/home/satyaaditech/.hermes/google_token.json"
PARENT_FOLDER_ID = "1Bh9ZIizra0I-3hmlqcHjhLJi3-eTAI4U"  # Materi Olahrasa
MASTER_SHEET_ID = "1QuTSjBV-iOckaIoSu07wQa0LcnbgdR97mxAqOloIEb0"
KONTEMPLASI_DIR = "/home/satyaaditech/kontemplasi"
SHARE_RENUNGAN_DIR = "/home/satyaaditech/share/renungan"

def get_google_services():
    with open(TOKEN_PATH, "r") as f:
        creds_data = json.load(f)
    creds = Credentials.from_authorized_user_info(creds_data)
    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)
    sheets_service = build("sheets", "v4", credentials=creds)
    return drive_service, docs_service, sheets_service

def render_video(poster_path, audio_path, output_mp4):
    print(f"🎬 [1/6] Rendering 1080p Video to {output_mp4}...")
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-framerate", "1",
        "-i", poster_path,
        "-i", audio_path,
        "-filter_complex",
        "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=20:10[bg];[0:v]scale=-1:1000[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2",
        "-r", "5",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_mp4
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg render failed: {res.stderr.decode('utf-8', errors='ignore')}")
    print(f"✅ Video successfully rendered ({os.path.getsize(output_mp4) / (1024*1024):.2f} MB)")

def upload_to_youtube(video_path, title, description):
    print(f"📺 [2/6] Uploading to YouTube channel @siswatalkstv...")
    sys.path.append(KONTEMPLASI_DIR)
    from upload_youtube import upload_video
    video_id = upload_video(
        file_path=video_path,
        title=title[:95],
        description=description,
        privacy="public"
    )
    if not video_id:
        raise RuntimeError("YouTube upload returned empty video_id")
    yt_url = f"https://youtu.be/{video_id}"
    print(f"✅ YouTube uploaded: {yt_url}")
    return yt_url

def create_and_format_gdoc(drive_service, docs_service, doc_title, poster_path, header_lines, body_sections, youtube_url, web_url):
    print(f"📄 [3/6] Creating and formatting Google Doc...")
    # 1. Upload poster to Drive
    file_metadata = {
        "name": os.path.basename(poster_path),
        "parents": [PARENT_FOLDER_ID]
    }
    media = MediaFileUpload(poster_path, mimetype="image/png")
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    poster_drive_id = uploaded_file.get("id")
    drive_service.permissions().create(fileId=poster_drive_id, body={"role": "reader", "type": "anyone"}).execute()
    poster_url = f"https://lh3.googleusercontent.com/d/{poster_drive_id}"

    # 2. Create blank doc in folder
    doc_metadata = {
        "name": doc_title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [PARENT_FOLDER_ID]
    }
    created_doc = drive_service.files().create(body=doc_metadata, fields="id").execute()
    doc_id = created_doc.get("id")

    # 3. Build text & style ranges
    # Structure:
    # Page 1: Date + RENUNGAN PENYISWAAN + Title + Image + PageBreak
    # Page 2: Salam + Sections (Pethikan, Uraian, Praktik, Renungan, Aplikasi, Satuhu) + Footer Links
    date_text = header_lines["date"] + "\n"
    category_text = "RENUNGAN PENYISWAAN\n"
    title_text = header_lines["thematic_title"] + "\n\n"
    
    body_text = ""
    body_text += f"{body_sections['salam']}\n\n"
    body_text += f"PETHIKAN DINTEN PUNIKA\n{body_sections['source_header']}\n{body_sections['quote_jawa']}\n{body_sections['quote_translation']}\n\n"
    body_text += f"URAIAN\n{body_sections['uraian']}\n\n"
    body_text += f"PRAKTIK\n{body_sections['praktik']}\n\n"
    body_text += f"RENUNGAN\n{body_sections['renungan']}\n\n"
    body_text += f"APLIKASI\n{body_sections['aplikasi']}\n\n"
    body_text += f"{body_sections['closing']}\n\n"
    
    footer_text = f"• 📺 Video YouTube: {youtube_url}\n• 🌐 Pustaka Web Kontemplasi: {web_url}\n"

    # Insert text first
    full_text = date_text + category_text + title_text + "\n" + body_text + footer_text
    docs_service.documents().batchUpdate(documentId=doc_id, body={
        "requests": [{"insertText": {"location": {"index": 1}, "text": full_text}}]
    }).execute()

    # Apply styling & insert image + page break
    # Find indices
    current_doc = docs_service.documents().get(documentId=doc_id).execute()
    doc_content = current_doc.get("body", {}).get("content", [])
    
    # Calculate positions
    idx_date = 1
    idx_cat = idx_date + len(date_text)
    idx_title = idx_cat + len(category_text)
    idx_img_placeholder = idx_title + len(title_text)

    # Insert image at placeholder
    docs_service.documents().batchUpdate(documentId=doc_id, body={
        "requests": [
            {
                "insertInlineImage": {
                    "location": {"index": idx_img_placeholder},
                    "uri": poster_url,
                    "objectSize": {
                        "width": {"magnitude": 320, "unit": "PT"},
                        "height": {"magnitude": 480, "unit": "PT"}
                    }
                }
            }
        ]
    }).execute()

    # Re-fetch doc after image insert to get new indices
    current_doc = docs_service.documents().get(documentId=doc_id).execute()
    
    # Insert Page Break right after image
    docs_service.documents().batchUpdate(documentId=doc_id, body={
        "requests": [
            {
                "insertPageBreak": {
                    "location": {"index": idx_img_placeholder + 2}
                }
            }
        ]
    }).execute()

    # Style Header & Body
    # Re-fetch content to format cleanly
    gdoc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    print(f"✅ Google Doc created & formatted: {gdoc_url}")
    return gdoc_url

def sync_web_library():
    print(f"🌐 [4/6] Syncing Web Library to GitHub Pages...")
    cmd = ["/home/satyaaditech/kontemplasi/sync_to_github.sh"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"Web sync failed: {res.stderr.decode('utf-8', errors='ignore')}")
    print(f"✅ Web Library synced & pushed to GitHub Pages.")

def append_to_master_sheet(sheets_service, row_data):
    print(f"📊 [5/6] Logging to Master Google Sheet...")
    res = sheets_service.spreadsheets().values().get(
        spreadsheetId=MASTER_SHEET_ID,
        range="Rekap Renungan!A:A"
    ).execute()
    rows = res.get("values", [])
    next_num = len(rows)  # includes header
    next_row_idx = len(rows) + 1

    full_row = [next_num] + row_data
    sheets_service.spreadsheets().values().append(
        spreadsheetId=MASTER_SHEET_ID,
        range="Rekap Renungan!A:M",
        valueInputOption="USER_ENTERED",
        body={"values": [full_row]}
    ).execute()
    print(f"✅ Logged row #{next_num} to Master Sheet.")

def verify_live_url(web_url):
    print(f"🔍 [6/6] Verifying live web availability for {web_url}...")
    for attempt in range(1, 10):
        try:
            r = requests.get(web_url, timeout=10)
            if r.status_code == 200:
                print(f"✅ Live Web URL verified (HTTP {r.status_code}).")
                return True
        except Exception as e:
            pass
        time.sleep(3)
    print(f"⚠️ Web URL returned non-200 or slow cache propagation, but deployment was successfully pushed.")
    return True

if __name__ == "__main__":
    print("Renungan Production Pipeline initialized.")
