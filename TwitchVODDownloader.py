#!/usr/bin/env python3
"""
Twitch VOD Downloader
Lädt das neueste VOD eines Twitch-Kanals herunter
"""

import json
import os
import requests
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

class TwitchVODDownloader:
    def __init__(self):
        # Lade Umgebungsvariablen aus .env Datei
        load_dotenv()
        
        # Validiere, dass alle erforderlichen Umgebungsvariablen gesetzt sind
        required_vars = ['TWITCH_CLIENT_ID', 'TWITCH_ACCESS_TOKEN', 'TWITCH_CHANNEL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print("Fehler: Folgende Umgebungsvariablen sind nicht gesetzt:")
            for var in missing_vars:
                print(f"  - {var}")
            print("\nStelle sicher, dass du eine .env Datei erstellt hast.")
            print("Kopiere .env.template zu .env und fülle deine Credentials ein.")
            sys.exit(1)
        
        # Lade Konfiguration aus Umgebungsvariablen
        self.config = {
            'channel': os.getenv('TWITCH_CHANNEL'),
            'quality': os.getenv('DOWNLOAD_QUALITY', '720p'),
            'output_directory': os.getenv('OUTPUT_DIRECTORY', './downloads'),
            'twitch': {
                'client_id': os.getenv('TWITCH_CLIENT_ID'),
                'access_token': os.getenv('TWITCH_ACCESS_TOKEN')
            }
        }
        
        self.headers = {
            'Client-ID': self.config['twitch']['client_id'],
            'Authorization': f'Bearer {self.config["twitch"]["access_token"]}'
        }
    
    def get_user_id(self, username):
        """Ermittelt die User-ID für einen Twitch-Benutzernamen"""
        url = "https://api.twitch.tv/helix/users"
        params = {"login": username}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code != 200:
            print(f"Fehler beim Abrufen der User-ID: {response.status_code}")
            return None
            
        data = response.json()
        if not data.get('data'):
            print(f"Benutzer '{username}' nicht gefunden!")
            return None
            
        return data['data'][0]['id']
    
    def get_latest_vod(self, user_id):
        """Holt das neueste VOD für eine User-ID"""
        url = "https://api.twitch.tv/helix/videos"
        params = {
            "user_id": user_id,
            "type": "archive",
            "first": 1
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code != 200:
            print(f"Fehler beim Abrufen der VODs: {response.status_code}")
            return None
            
        data = response.json()
        if not data.get('data'):
            print("Keine VODs gefunden!")
            return None
            
        return data['data'][0]
    
    def sanitize_filename(self, filename):
        """Bereinigt Dateinamen von ungültigen Zeichen"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def download_vod(self, vod_url, output_path, quality):
        """Lädt das VOD mit streamlink herunter"""
        quality_map = {
            "best": "best",
            "720p": "720p60,720p,worst",
            "480p": "480p,worst",
            "worst": "worst"
        }
        
        selected_quality = quality_map.get(quality, "best")
        
        cmd = [
            "streamlink",
            vod_url,
            selected_quality,
            "--output", output_path,
            "--retry-streams", "5",
            "--retry-max", "3"
        ]
        
        print(f"Starte Download mit Qualität: {quality}")
        print(f"Ausgabedatei: {output_path}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("Download erfolgreich abgeschlossen!")
                return True
            else:
                print(f"Fehler beim Download: {result.stderr}")
                return False
        except FileNotFoundError:
            print("Streamlink ist nicht installiert oder nicht im PATH!")
            print("Installiere streamlink mit: pip install streamlink")
            return False
    
    def run(self):
        """Hauptfunktion zum Ausführen des Downloads"""
        channel = self.config['channel']
        quality = self.config['quality']
        output_dir = self.config['output_directory']
        
        print(f"Suche nach dem neuesten VOD für Kanal: {channel}")
        
        # User-ID ermitteln
        user_id = self.get_user_id(channel)
        if not user_id:
            return
        
        # Neuestes VOD abrufen
        vod = self.get_latest_vod(user_id)
        if not vod:
            return
        
        # VOD-Informationen
        vod_id = vod['id']
        title = vod['title']
        created_at = vod['created_at']
        duration = vod['duration']
        vod_url = vod['url']
        
        print(f"\nGefundenes VOD:")
        print(f"Titel: {title}")
        print(f"Erstellt: {created_at}")
        print(f"Dauer: {duration}")
        print(f"URL: {vod_url}")
        
        # Ausgabeverzeichnis erstellen
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Dateiname generieren
        timestamp = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%Y%m%d_%H%M%S')
        safe_title = self.sanitize_filename(title)[:50]  # Titel auf 50 Zeichen begrenzen
        filename = f"{channel}_{timestamp}_{safe_title}.mp4"
        output_path = os.path.join(output_dir, filename)
        
        # Titel in separate Datei speichern
        title_file = os.path.join(output_dir, f"{channel}_{timestamp}_title.txt")
        with open(title_file, 'w', encoding='utf-8') as f:
            f.write(f"Kanal: {channel}\n")
            f.write(f"Titel: {title}\n")
            f.write(f"Erstellt: {created_at}\n")
            f.write(f"Dauer: {duration}\n")
            f.write(f"VOD-ID: {vod_id}\n")
            f.write(f"URL: {vod_url}\n")
        
        print(f"\nTitel-Informationen gespeichert in: {title_file}")
        
        # VOD herunterladen
        success = self.download_vod(vod_url, output_path, quality)
        
        if success:
            print(f"\nDownload abgeschlossen!")
            print(f"Video: {output_path}")
            print(f"Titel: {title_file}")
        else:
            print("\nDownload fehlgeschlagen!")

def main():
    downloader = TwitchVODDownloader()
    downloader.run()

if __name__ == "__main__":
    main()
