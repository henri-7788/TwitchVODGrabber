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

## 3. Konfiguration (SICHER)

**WICHTIG**: Deine Twitch API-Credentials werden jetzt sicher in einer `.env` Datei gespeichert, die nicht auf GitHub gepusht wird.

### Schritt 1: .env Datei erstellen
```bash
cp .env.template .env
```

### Schritt 2: .env Datei bearbeiten
Öffne die `.env` Datei und fülle deine echten Credentials ein:

```env
# Twitch API Credentials
TWITCH_CLIENT_ID=deine_echte_client_id_hier
TWITCH_ACCESS_TOKEN=dein_echter_access_token_hier
TWITCH_CHANNEL=montanablack88
DOWNLOAD_QUALITY=720p
OUTPUT_DIRECTORY=./downloads
```

### Verfügbare Qualitätsstufen:
- `"best"` - Beste verfügbare Qualität
- `"720p"` - 720p (falls verfügbar, sonst schlechtere)
- `"480p"` - 480p (falls verfügbar, sonst schlechteste)
- `"worst"` - Schlechteste verfügbare Qualität

## 4. Verwendung

```bash
python TwitchVODDownloader.py
```

Das Skript wird:
1. Das neueste VOD des konfigurierten Kanals finden
2. Es in der gewählten Qualität herunterladen
3. Eine Textdatei mit den VOD-Informationen erstellen

## 5. Ausgabe

Die Downloads werden im konfigurierten Verzeichnis gespeichert:
- **Video**: `kanal_datum_titel.mp4`
- **Info**: `kanal_datum_title.txt`

## Sicherheit

- Die `.env` Datei enthält deine sensiblen API-Credentials und wird **NICHT** auf GitHub gepusht
- Die `.gitignore` Datei sorgt dafür, dass sensible Dateien ausgeschlossen werden
- Verwende niemals echte Credentials in der `.env.template` Datei

## Fehlerbehebung

### "Folgende Umgebungsvariablen sind nicht gesetzt"
Stelle sicher, dass du eine `.env` Datei erstellt und alle erforderlichen Variablen ausgefüllt hast.

### "Streamlink ist nicht installiert"
```bash
pip install streamlink
```

### "Fehler beim Abrufen der User-ID: 401"
Dein Access Token ist ungültig oder abgelaufen. Generiere einen neuen Token.

### "Benutzer nicht gefunden"
Überprüfe die Schreibweise des Kanal-Namens in der `.env` Datei.

## GitHub Push

Du kannst jetzt sicher auf GitHub pushen, ohne dass deine API-Credentials preisgegeben werden:

```bash
git add .
git commit -m "Secure credential management with environment variables"
git push
```

Die `.env` Datei wird automatisch ignoriert und nicht hochgeladen.
