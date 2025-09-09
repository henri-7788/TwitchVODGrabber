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

### Schritt 3: Client ID und Client Secret erhalten
1. Öffne deine erstellte Anwendung
2. Kopiere die **Client ID**
3. Klicke auf "New Secret" und kopiere das **Client Secret**

**WICHTIG**: Du brauchst jetzt KEINEN manuellen Access Token mehr! Das Skript generiert automatisch App Access Tokens.

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
TWITCH_CLIENT_SECRET=dein_echtes_client_secret_hier
TWITCH_CHANNEL=montanablack88
DOWNLOAD_QUALITY=720p
OUTPUT_DIRECTORY=./downloads

# Test Mode (True/False) - Begrenzt Downloads auf 30 Sekunden für schnelle Tests
TEST_MODE=False
```

### Verfügbare Qualitätsstufen:
- `"best"` - Beste verfügbare Qualität
- `"720p"` - 720p (falls verfügbar, sonst schlechtere)
- `"480p"` - 480p (falls verfügbar, sonst schlechteste)
- `"worst"` - Schlechteste verfügbare Qualität

### Test Mode:
- `TEST_MODE=True` - Downloads werden nach 30 Sekunden gestoppt (perfekt zum Testen)
- `TEST_MODE=False` - Normale Downloads ohne Zeitbegrenzung

## 4. Verwendung

```bash
python TwitchVODDownloader.py
```

Das Skript wird:
1. Automatisch einen App Access Token generieren
2. Das neueste VOD des konfigurierten Kanals finden
3. Es in der gewählten Qualität herunterladen
4. **Einen Fortschrittsbalken während des Downloads anzeigen**
5. Eine Textdatei mit den VOD-Informationen erstellen

## 5. Ausgabe

Die Downloads werden im konfigurierten Verzeichnis gespeichert:
- **Video**: `kanal_datum_titel.mp4` (oder `_TEST.mp4` im Test Mode)
- **Info**: `kanal_datum_title.txt`

## 6. Neue Features

### 🧪 Test Mode
- Setze `TEST_MODE=True` in der `.env` Datei
- Downloads werden automatisch nach 30 Sekunden gestoppt
- Perfekt zum Testen der Funktionalität ohne lange Downloads
- Dateien werden mit `_TEST.mp4` Suffix gespeichert

### 📊 Fortschrittsbalken
- Zeigt Download-Fortschritt in Echtzeit
- Anzeige von:
  - Prozentualer Fortschritt
  - Heruntergeladene MB / Gesamtgröße
  - Download-Geschwindigkeit (MB/s)
  - Geschätzte verbleibende Zeit (ETA)
- Aktualisiert sich alle 0.5 Sekunden

### Beispiel-Fortschrittsbalken:
```
Download: |██████████████████████████████████████████████████| 100.0% (150.2MB/150.2MB) 5.2MB/s ETA: 0s
Download abgeschlossen! 150.2MB in 28.9s (5.2MB/s)
```

## Sicherheit

- Die `.env` Datei enthält deine sensiblen API-Credentials und wird **NICHT** auf GitHub gepusht
- Die `.gitignore` Datei sorgt dafür, dass sensible Dateien ausgeschlossen werden
- Verwende niemals echte Credentials in der `.env.template` Datei
- **Automatische Token-Verwaltung**: Das Skript generiert und erneuert automatisch App Access Tokens

## Vorteile der neuen Version

✅ **Keine manuellen Access Tokens mehr nötig**
✅ **Automatische Token-Erneuerung bei 401-Fehlern**
✅ **Einfachere Einrichtung mit nur Client ID und Secret**
✅ **Robuster gegen Token-Abläufe**
✅ **Test Mode für schnelle Tests**
✅ **Fortschrittsbalken für bessere Übersicht**

## Fehlerbehebung

### "TWITCH_CLIENT_ID ist nicht gesetzt"
Stelle sicher, dass du eine `.env` Datei erstellt und alle erforderlichen Variablen ausgefüllt hast.

### "TWITCH_CLIENT_SECRET ist nicht gesetzt"
Füge dein Client Secret zur `.env` Datei hinzu.

### "Streamlink ist nicht installiert"
```bash
pip install streamlink
```

### "Benutzer nicht gefunden"
Überprüfe die Schreibweise des Kanal-Namens in der `.env` Datei.

## GitHub Push

Du kannst jetzt sicher auf GitHub pushen, ohne dass deine API-Credentials preisgegeben werden:

```bash
git add .
git commit -m "Added test mode and progress bar features"
git push
```

Die `.env` Datei wird automatisch ignoriert und nicht hochgeladen.
