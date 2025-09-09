# Twitch VOD Downloader - Setup Anleitung

## 1. Installation der Abhängigkeiten

```bash
pip install -r requirements.txt
```

## 2. Twitch API Einrichtung

Um das Skript zu verwenden, benötigst du Twitch API-Credentials:

### Schritt 1: Twitch Developer Account
1. Gehe zu [dev.twitch.tv](https://dev.twitch.tv/)
2. Melde dich mit deinem Twitch-Account an
3. Klicke auf "Your Console"

### Schritt 2: Anwendung registrieren
1. Klicke auf "Register Your Application"
2. Fülle die Felder aus:
   - **Name**: Ein beliebiger Name für deine App
   - **OAuth Redirect URLs**: `http://localhost`
   - **Category**: Wähle eine passende Kategorie
3. Erstelle die Anwendung

### Schritt 3: Client ID erhalten
1. Öffne deine erstellte Anwendung
2. Kopiere die **Client ID**

### Schritt 4: Access Token generieren
1. Öffne diese URL in deinem Browser (ersetze `DEINE_CLIENT_ID`):
```
https://id.twitch.tv/oauth2/authorize?client_id=DEINE_CLIENT_ID&redirect_uri=http://localhost&response_type=token&scope=
```
2. Autorisiere die Anwendung
3. Du wirst zu `http://localhost/#access_token=...` weitergeleitet
4. Kopiere den **Access Token** aus der URL

## 3. Konfiguration

Bearbeite die `config.json` Datei:

```json
{
    "channel": "montanablack88",
    "quality": "720p",
    "output_directory": "./downloads",
    "twitch": {
        "client_id": "deine_echte_client_id_hier",
        "access_token": "dein_echter_access_token_hier"
    }
}
```

### Verfügbare Qualitätsstufen:
- `"best"` - Beste verfügbare Qualität
- `"720p"` - 720p (falls verfügbar, sonst schlechtere)
- `"480p"` - 480p (falls verfügbar, sonst schlechteste)
- `"worst"` - Schlechteste verfügbare Qualität

## 4. Verwendung

```bash
python twitch_vod_downloader.py
```

Das Skript wird:
1. Das neueste VOD des konfigurierten Kanals finden
2. Es in der gewählten Qualität herunterladen
3. Eine Textdatei mit den VOD-Informationen erstellen

## 5. Ausgabe

Die Downloads werden im konfigurierten Verzeichnis gespeichert:
- **Video**: `kanal_datum_titel.mp4`
- **Info**: `kanal_datum_title.txt`

## Fehlerbehebung

### "Streamlink ist nicht installiert"
```bash
pip install streamlink
```

### "Konfigurationsdatei nicht gefunden"
Stelle sicher, dass die `config.json` im gleichen Verzeichnis wie das Skript liegt.

### "Fehler beim Abrufen der User-ID: 401"
Dein Access Token ist ungültig oder abgelaufen. Generiere einen neuen Token.

### "Benutzer nicht gefunden"
Überprüfe die Schreibweise des Kanal-Namens in der config.json.