#!/usr/bin/env python3
import os
import sys
import json
import argparse
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

TOKEN_PATH = "/home/satyaaditech/.config/youtube/token.json"

def get_authenticated_service():
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Token file not found at {TOKEN_PATH}. Run OAuth flow first.")
        
    with open(TOKEN_PATH) as f:
        token_data = json.load(f)
        
    creds = Credentials.from_authorized_user_info(token_data)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
            
    return build('youtube', 'v3', credentials=creds)

def upload_video(file_path, title, description, tags=None, privacy="unlisted"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video file not found at {file_path}")
        
    youtube = get_authenticated_service()
    
    if tags is None:
        tags = ['Pangestu', 'Sasangka Jati', 'Renungan Harian', 'Penyiswaan', 'Olahrasa']
        
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': privacy,
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(file_path, mimetype='video/mp4', resumable=True)
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = request.execute()
    video_id = response.get('id')
    share_url = f"https://youtu.be/{video_id}"
    return {
        "video_id": video_id,
        "url": share_url,
        "title": title,
        "status": privacy
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload Renungan Video to YouTube")
    parser.add_argument("--file", required=True, help="Path to mp4 video")
    parser.add_argument("--title", required=True, help="Video title")
    parser.add_argument("--desc", default="", help="Video description")
    parser.add_argument("--privacy", default="unlisted", choices=["public", "unlisted", "private"])
    
    args = parser.parse_args()
    res = upload_video(args.file, args.title, args.desc, privacy=args.privacy)
    print(json.dumps(res, indent=2))
