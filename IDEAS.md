# pwnamap — Ideen & To-Do

> Persistenter Backlog für Features, Verbesserungen und Fragen, die du noch absegnen musst.
> Stand: vibecoded-Branch, nach Datumsfilter-Implementierung.

---

## Aktuell in Arbeit (dieser Branch)

- [x] Datumsfilter für /explore (Data Explorer)
- [x] Datumsfilter für /pwnamap (Hauptkarte)
  - Datumsbereich (date_from, date_to) wird im Backend an wigle.time gefiltert
  - Quick-Presets: Last 24h, Last 7d, Last 30d, All
  - Custom-Range mit zwei date-Inputs
  - URL-Parameter persistent -> teilbarer Link mit Filter

---

## Kurzfristig (PR-tauglich, ~1-2 Tage Arbeit pro Punkt)

### 1. Heatmap-Layer auf der Karte
- Warum: Cluster sind gut, aber eine Heatmap zeigt Dichte viel intuitiver
- Aufwand: Leaflet.heat als zusaetzliche Dep, Toggle-Button im Map-Header, Layer-Control
- Bestaetigt? [ ]

### 2. Export der Karte (GeoJSON / KML)
- Warum: User wollen ihre Daten weiterverwenden (z.B. fuer GIS, eigene Tools)
- Aufwand: Kleine Backend-Route, Button in der UI, Streaming-Response
- Bestaetigt? [ ]

### 3. Bessere Pwnagotchi-Stats
- README erwaehnt "More information about your pwnagotchi" als Coming Soon
- /api/pwned hat aktuell keine Quelle fuer Pwnagotchi-Metadaten
- Plugin erweitern um pwnagotchi_name, pwnagotchi_version, last_seen
- Bestaetigt? [ ]

### 4. Zeitreihen-Charts
- Cracked networks per week/month Chart (Chart.js, selbst gehostet)
- Backend aggregiert nach Woche, Frontend rendert Sparkline
- Bestaetigt? [ ]

### 5. Filter-Presets speichern
- Benannte Filter-Sets anlegen (Mein Kiez, Nur WPA3)
- Bestaetigt? [ ]

---

## Mittelfristig (Architektur-Cleanup)

### 6. Tool-Runner refactoren
- Aktuell: subprocess.Popen("python -u tool.py") - haesslich, schwer testbar
- Vorschlag: Tools als importierbare Module mit run(stdout, db, creds)
- Bestaetigt? [ ]

### 7. Echte Progress-Reports bei Tools
- Strukturiertes JSON-Streaming mit {phase, percent, message} Events
- Frontend: Progressbars statt nur Text-Scrolling
- Bestaetigt? [ ]

### 8. Hintergrund-Jobs fuer lange Tool-Runs
- wpasec-Sync mit 50k Networks dauert Minuten
- RQ oder APScheduler als Background-Worker
- Bestaetigt? [ ]

### 9. Multi-User-Support
- Aktuell Single-User, aber users-Tabelle existiert
- Pro User eigene Credentials und pwned/wigle-Daten
- Bestaetigt? [ ]

---

## Nice-to-have

### 10. Dark/Light-Theme-Toggle - [ ]
### 11. i18n / Mehrsprachigkeit (DE/EN) - [ ]
### 12. PWA-Update-Benachrichtigung - [ ]
### 13. Map-Bounds-Filter (Performance fuer 50k+ Netze) - [ ]
### 14. Markierungs-Icons nach Encryption-Typ (WPA3 gruen, offen rot) - [ ]
### 15. Signal-Staerke-Anzeige im Popup (Ampelsystem) - [ ]
### 16. SSID-Suche mit RegEx - [ ]
### 17. Time-Machine-Ansicht (Slider durch die Zeit) - [ ]
### 18. Hotspot-Detection (Cluster-Analyse) - [ ]
### 19. Wigle-API v3 statt v2 checken - [ ]
### 20. Backup/Restore Button (SQLite .backup Command) - [ ]

---

## Bekannte Issues / Tech Debt

- Tools nutzen hardcoded app/data/pwnamap.db statt get_db() - zentralisieren
- /api/explore ohne Pagination - bei 100k+ Rows haengts
- dynamic.py nutzt os.listdir fuer Handshakes - keine Filter
- auth.py: kein CSRF-Token
- pwnamap.js hardcoded network_type=WIFI - sollte konfigurierbar sein
- Frontend-Bundle im Repo? Muss raus aus .gitignore
- Tests fehlen komplett

---

## Offene Fragen

1. Wollen wir das Plugin-Repo auch anpassen oder hier nur API-faehig bauen?
2. Filter-Presets pro User oder global?
3. Realistische Obergrenze fuer Networks? Beeinflusst Pagination
4. Performance-Budget: Wie lange darf Map-Load bei 10k/100k/1M dauern?

---

## Aenderungslog

| Datum | Aenderung | Commit |
|-------|----------|--------|
| 2026-06-23 | Datumsfilter implementiert | (pending) |
