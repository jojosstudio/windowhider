# Window Hider for macOS

> Window Hider portiert für macOS

⚠️ **Wichtig:** Diese Version funktioniert anders als die Windows-Version, da macOS keine direkte Entsprechung zu `SetWindowDisplayAffinity` hat.

## Funktionsweise

Statt Fenster vor dem Stream zu verstecken, werden sie auf macOS **minimiert oder ausgeblendet**. Das ist die beste verfügbare Lösung für macOS.

## Systemanforderungen

- macOS 10.12 oder höher
- Python 3.8+ (für den Build)

## Installation

### Für Endnutzer

1. Lade `WindowHider-macOS.dmg` herunter
2. Öffne die DMG-Datei
3. Ziehe "Window Hider" in den Applications-Ordner
4. Starte Window Hider aus dem Applications-Ordner

### Für Entwickler (Build from Source)

```bash
# 1. Repository klonen
git clone https://github.com/jojosstudio/windowhider.git
cd windowhider

# 2. Abhängigkeiten installieren
pip3 install py2app pyobjc-framework-Cocoa pyobjc-framework-Quartz

# 3. Build ausführen
chmod +x build_mac.sh
./build_mac.sh
```

## Dateien

- `windowshider_macos.py` - Hauptanwendung
- `setup_mac.py` - py2app Konfiguration
- `build_mac.sh` - Build-Skript

## Unterschiede zur Windows-Version

| Feature | Windows | macOS |
|---------|---------|-------|
| Hide from Stream | ✅ Native (SetWindowDisplayAffinity) | ⚠️ Minimieren/Ausblenden |
| DLL Injection | ✅ Ja | ❌ Nein (Sandbox) |
| Admin-Rechte | ✅ Benötigt | ⚠️ Accessibility-Berechtigung |

## Troubleshooting

### "Window Hider" kann nicht geöffnet werden

1. Rechtsklick auf die App → "Öffnen"
2. Oder: Systemeinstellungen → Sicherheit → "Trotzdem öffnen"

### Keine Fenster in der Liste

Die App benötigt **Accessibility-Berechtigungen**:
1. Systemeinstellungen → Sicherheit & Datenschutz → Datenschutz → Bedienungshilfen
2. Füge "Window Hider" hinzu

## Lizenz

MIT License - Siehe [LICENSE.txt](LICENSE.txt)

---

Entwickelt mit Unterstützung von Kimi K2.5
