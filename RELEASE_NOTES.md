# Window Hider v1.5.0 - Release Notes

## 🎉 Neue Features

### Self-Hide
- **Programm kann sich selbst verstecken**: Window Hider kann sich nun selbst vor dem Stream verstecken
- **Auto-Hide bei Start**: Option "Hide Self from Stream" in den Einstellungen versteckt die App automatisch beim Start
- **Status-Anzeige**: Zeigt im Status-Label an wenn das Programm selbst versteckt ist

### Aufgeräumtes Beenden
- **Automatisches Cleanup**: Beim Schließen des Programms werden alle versteckten Fenster automatisch wieder angezeigt
- **Keine versteckten Fenster mehr**: Fenster bleiben nicht mehr versteckt wenn das Programm beendet wird

### Icon & Branding
- **Neues App-Icon**: Modernes Icon mit Eye-Design (grün/rot/weiß Farbschema)
- **Multi-Size Icon**: ICO-Datei mit 16px bis 256px für alle Anwendungsfälle
- **Icon-Preview**: PNG-Version für Dokumentation

### Installer
- **Windows Installer**: Professioneller Inno Setup Installer (.exe)
- **Admin-Rechte**: Installer fragt automatisch nach Administrator-Rechten
- **Startmenü-Eintrag**: Programm erscheint im Windows Startmenü
- **Desktop-Icon**: Optionales Desktop-Shortcut während Installation
- **Deutsch/Englisch**: Installer unterstützt beide Sprachen

### Website
- **GitHub Pages**: Neue Projekt-Website unter https://jojosstudio.github.io/windowhider/
- **Feature-Übersicht**: Alle Funktionen auf einer Seite dargestellt
- **Responsive Design**: Funktioniert auf Desktop und Mobile

### Dokumentation
- **README aktualisiert**: Website-Link hinzugefügt
- **LICENSE.txt**: MIT Lizenz hinzugefügt

## 🔧 Technische Änderungen

### Build-System
- **PyInstaller Spec**: Aktualisiert für Icon-Support und DLL-Einbindung
- **EXE mit Icon**: Fertige EXE enthält nun das App-Icon
- **Single-File EXE**: Alle Dependencies in einer Datei

### Installer-Skript
- **Inno Setup Script**: Vollständig konfiguriertes `.iss` Skript
- **Auto-Start Option**: Programm kann nach Installation direkt gestartet werden
- **Uninstaller**: Automatische Deinstallation über Systemsteuerung

## 📦 Dateien

```
windowhider/
├── WindowHider.exe          # Fertige Anwendung
├── WindowHider-Setup.exe    # Windows Installer
├── icon.ico                 # App-Icon
├── icon_preview.png         # Icon-Vorschau
├── installer.iss            # Inno Setup Script
├── index.html               # Projekt-Website
├── create_icon.py           # Icon-Generator Script
├── README.md                # Aktualisiert mit Website-Link
├── LICENSE.txt              # MIT Lizenz
└── window_hider.spec        # PyInstaller Konfiguration
```

## 🚀 Installation

### Variante 1: Installer (Empfohlen)
1. `WindowHider-Setup.exe` herunterladen
2. Als Administrator ausführen
3. Installation folgen
4. Programm über Startmenü starten

### Variante 2: Portable
1. `WindowHider.exe` herunterladen
2. Als Administrator ausführen

## 📝 Bekannte Einschränkungen

- **Auto-Start nach Installation**: Der Installer kann das Programm nicht direkt starten (Admin-Rechte erforderlich). Bitte über Startmenü starten.
- **Windows 10/11 only**: Funktioniert nicht auf älteren Windows-Versionen
- **Admin-Rechte erforderlich**: Programm muss als Administrator laufen

---

**Entwickelt von Jojosstudio - 2026**
