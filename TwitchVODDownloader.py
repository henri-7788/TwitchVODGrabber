#!/usr/bin/env python3
"""
Twitch VOD Downloader
Lädt das neueste VOD eines Twitch-Kanals herunter
"""

# --- am Anfang von TwitchVODDownloader.py ---
import os, requests
from pathlib import Path
from dotenv import load_dotenv
import subprocess
import sys
from datetime import datetime
import time
import threading

# .env sicher laden (relativ zur Datei)
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID") or os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET") or os.getenv("CLIENT_SECRET")

_token = None

def _get_app_access_token():
    r = requests.post(
        "https://id.twitch.tv/oauth2/token",
        data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "grant_type": "client_credentials"},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()["access_token"]

def helix_get(path, params=None):
    """GET https://api.twitch.tv/helix/<path> mit korrekten Headers; refresht Token bei 401."""
    global _token
    if not _token:
        _token = _get_app_access_token()

    headers = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {_token}"}
    url = f"https://api.twitch.tv/helix/{path}"
    r = requests.get(url, params=params, headers=headers, timeout=20)

    if r.status_code == 401:  # abgelaufener/inkonsistenter Token -> neu holen und 1x retry
        _token = _get_app_access_token()
        headers["Authorization"] = f"Bearer {_token}"
        r = requests.get(url, params=params, headers=headers, timeout=20)

    r.raise_for_status()
    return r.json()

class ProgressBar:
    """Einfacher Fortschrittsbalken für Downloads"""
    def __init__(self, total_size=None):
        self.total_size = total_size
        self.downloaded = 0
        self.start_time = time.time()
        self.last_update = 0
        
    def update(self, downloaded_bytes):
        """Aktualisiert den Fortschrittsbalken"""
        self.downloaded = downloaded_bytes
        current_time = time.time()
        
        # Nur alle 0.5 Sekunden aktualisieren
        if current_time - self.last_update < 0.5:
            return
            
        self.last_update = current_time
        
        if self.total_size:
            percent = (downloaded_bytes / self.total_size) * 100
            bar_length = 50
            filled_length = int(bar_length * downloaded_bytes // self.total_size)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            # Geschwindigkeit berechnen
            elapsed_time = current_time - self.start_time
            if elapsed_time > 0:
                speed = downloaded_bytes / elapsed_time / 1024 / 1024  # MB/s
                eta = (self.total_size - downloaded_bytes) / (downloaded_bytes / elapsed_time) if downloaded_bytes > 0 else 0
                print(f'\rDownload: |{bar}| {percent:.1f}% ({downloaded_bytes/1024/1024:.1f}MB/{self.total_size/1024/1024:.1f}MB) {speed:.1f}MB/s ETA: {eta:.0f}s', end='', flush=True)
        else:
            # Ohne bekannte Gesamtgröße
            print(f'\rDownload: {downloaded_bytes/1024/1024:.1f}MB downloaded...', end='', flush=True)
    
    def finish(self):
        """Beendet den Fortschrittsbalken"""
        elapsed_time = time.time() - self.start_time
        print(f'\rDownload abgeschlossen! {self.downloaded/1024/1024:.1f}MB in {elapsed_time:.1f}s ({self.downloaded/1024/1024/elapsed_time:.1f}MB/s)')
        print()  # Neue Zeile

class TwitchVODDownloader:
    def __init__(self):
        # Validiere, dass alle erforderlichen Umgebungsvariablen gesetzt sind
        if not CLIENT_ID:
            print("Fehler: TWITCH_CLIENT_ID ist nicht gesetzt!")
            print("Stelle sicher, dass du eine .env Datei erstellt hast.")
            sys.exit(1)
            
        if not CLIENT_SECRET:
            print("Fehler: TWITCH_CLIENT_SECRET ist nicht gesetzt!")
            print("Stelle sicher, dass du eine .env Datei erstellt hast.")
            sys.exit(1)
        
        # Lade Konfiguration aus Umgebungsvariablen
        self.config = {
            'channel': os.getenv('TWITCH_CHANNEL'),
            'quality': os.getenv('DOWNLOAD_QUALITY', '720p'),
            'output_directory': os.getenv('OUTPUT_DIRECTORY', './downloads'),
            'test_mode': os.getenv('TEST_MODE', 'False').lower() in ('true', '1', 'yes', 'on'),
        }
        
        if not self.config['channel']:
            print("Fehler: TWITCH_CHANNEL ist nicht gesetzt!")
            print("Stelle sicher, dass du eine .env Datei erstellt hast.")
            sys.exit(1)
        
        if self.config['test_mode']:
            print("🧪 TEST MODE AKTIVIERT - Downloads werden auf 30 Sekunden begrenzt!")
    
    def get_user_id(self, username):
        """Ermittelt die User-ID für einen Twitch-Benutzernamen"""
        try:
            data = helix_get("users", params={"login": username})
            if not data.get('data'):
                print(f"Benutzer '{username}' nicht gefunden!")
                return None
            return data['data'][0]['id']
        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Abrufen der User-ID: {e}")
            return None
    
    def get_latest_vod(self, user_id):
        """Holt das neueste VOD für eine User-ID"""
        try:
            data = helix_get("videos", params={
                "user_id": user_id,
                "type": "archive",
                "first": 1
            })
            if not data.get('data'):
                print("Keine VODs gefunden!")
                return None
            return data['data'][0]
        except requests.exceptions.RequestException as e:
            print(f"Fehler beim Abrufen der VODs: {e}")
            return None
    
    def sanitize_filename(self, filename):
        """Bereinigt Dateinamen von ungültigen Zeichen"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def download_vod_with_progress(self, vod_url, output_path, quality):
        """Lädt das VOD mit streamlink herunter und zeigt Fortschritt"""
        quality_map = {
            "best": "best",
            "720p": "720p60,720p,worst",
            "480p": "480p,worst",
            "worst": "worst"
        }
        
        selected_quality = quality_map.get(quality, "best")
        
        # Test Mode: Begrenze Download auf 30 Sekunden
        if self.config['test_mode']:
            print("🧪 Test Mode: Download wird nach 30 Sekunden gestoppt")
            cmd = [
                "streamlink",
                vod_url,
                selected_quality,
                "--output", output_path,
                "--retry-streams", "5",
                "--retry-max", "3",
                "--stream-timeout", "30"  # Stoppt nach 30 Sekunden
            ]
        else:
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
            # Starte den Download-Prozess
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Fortschrittsbalken
            progress_bar = ProgressBar()
            start_time = time.time()
            
            # Überwache den Prozess
            while process.poll() is None:
                # Prüfe ob Datei existiert und wächst
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    progress_bar.update(file_size)
                
                time.sleep(0.5)  # Update alle 0.5 Sekunden
                
                # Test Mode: Stoppe nach 30 Sekunden
                if self.config['test_mode'] and (time.time() - start_time) > 30:
                    print(f"\n🧪 Test Mode: Download nach 30 Sekunden gestoppt")
                    process.terminate()
                    progress_bar.finish()
                    return True
            
            # Warte auf Prozess-Ende
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                progress_bar.finish()
                print("Download erfolgreich abgeschlossen!")
                return True
            else:
                print(f"Fehler beim Download: {stderr}")
                return False
                
        except FileNotFoundError:
            print("Streamlink ist nicht installiert oder nicht im PATH!")
            print("Installiere streamlink mit: pip install streamlink")
            return False
        except Exception as e:
            print(f"Unerwarteter Fehler beim Download: {e}")
            return False
    
    def run(self):
        """Hauptfunktion zum Ausführen des Downloads"""
        channel = self.config['channel']
        quality = self.config['quality']
        output_dir = self.config['output_directory']
        test_mode = self.config['test_mode']
        
        print(f"Suche nach dem neuesten VOD für Kanal: {channel}")
        if test_mode:
            print("🧪 TEST MODE: Downloads werden auf 30 Sekunden begrenzt")
        
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
        
        if test_mode:
            filename = f"{channel}_{timestamp}_{safe_title}_TEST.mp4"
        else:
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
            if test_mode:
                f.write(f"Test Mode: Ja (30 Sekunden Download)\n")
        
        print(f"\nTitel-Informationen gespeichert in: {title_file}")
        
        # VOD herunterladen
        success = self.download_vod_with_progress(vod_url, output_path, quality)
        
        if success:
            print(f"\nDownload abgeschlossen!")
            print(f"Video: {output_path}")
            print(f"Titel: {title_file}")
            if test_mode:
                print("🧪 Test Mode: Datei wurde nach 30 Sekunden gestoppt")
        else:
            print("\nDownload fehlgeschlagen!")

def main():
    downloader = TwitchVODDownloader()
    downloader.run()

if __name__ == "__main__":
    main()
