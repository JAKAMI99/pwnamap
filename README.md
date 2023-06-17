# Automated Pwnagotchi Handshake Map

---

## Idea
A selfhosted(!) map which shows Network-APs, where your pwnagotchi captured a handshake for. 

---
## ToDo
- [x] Automate CSV Export from onlinehashcrack.com
- [x] Detect changes in CSV Export 
- [ ] Detect new entries instead of changes
- [x] Wigle.net API : Get geolocations
- [x] Generate a map and plot POIs
- [ ] Make deployable
- Manual alternative for retrieving 
    - [ ] Handshakes (BSSIDs) - pwnagotchi plugin(?)
    - [ ] Geodata (own wardriving data) 

## Fix
- [ ] Error when authentication didn't work on onlinehashcrack.com



## Workflow getting bssid data
There are two different ideas of data retrieval. 

### Fully "automatic" but third-party-dependent way:
1. Autoupload captured handshakes to onlinehashcrack with the pwnagotchi **[Plugin](https://github.com/evilsocket/pwnagotchi/blob/master/pwnagotchi/plugins/default/onlinehashcrack.py)**
2. Get *auto-uploaded* handshakes and cracked passwords from onlinehashcrack. Works flawless with the "download_csv.py script"- ~~There is an API available, not sure if suitable for requesting. Might have to use web scraping **[API Docs](https://api.onlinehashcrack.com/)**~~
3. Parse the mac-address out of the API-request together with the BSSID, AP-Vendor, Date added and if found the cracked password.

### Manual uploading
1. Manually upload the handshakes to a web server trough eg. sFTP/custom pwnagotchi plugin.
2. Parse the mac-address and date captured out of the .pcap/.cap files. Could be automated with "folder change detection".

---

## Getting a geolocation trough mac-adresses

1. Request geolocation on wigle with the parsed mac-adress. **[API Docs](https://api.wigle.net/)**
2. If geolocation is found, which is highly likely if **[Wardriving](https://en.wikipedia.org/wiki/Wardriving)** was enabled while the Pwnagotchi was running, parse it together with the other data points.

---

## Current Dependencies
- requests (API)
- pandas (CSV)
- folium (Map)
```
pip3 install requests, pandas, folium
```

## Usage
Provide your wigle.net API key and your onlinehashcrack.com mail adress in the main.py.
```python3 main.py```

Open the created map.html