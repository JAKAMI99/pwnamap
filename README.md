# Automated Pwnagotchi Handshake Map

---

## Idea
A selfhosted(!) map which shows all captured handshakes and highlights those which are successfully got cracked. (red/green POIs)

---

## Workflow getting data
There are two different ideas of data retrieval. 

### Fully "automatic" but third-party-dependent way:
1. Autoupload caputured handshakes to onlinehashcrack with the pwnagotchi **[Plugin](https://github.com/evilsocket/pwnagotchi/blob/master/pwnagotchi/plugins/default/onlinehashcrack.py)**
2. Get *auto-uploaded* handshakes and cracked passwords from onlinehashcrack. There is an API available, not sure if suitable for requesting. Might have to use web scraping **[API Docs](https://api.onlinehashcrack.com/)**
3. Parse the mac-adress out of the API-request together with the BSSID, AP-Vendor, Date added and if found the cracked password.

### Manual uploading
1. Manually upload the handshakes to the webserver trough eg. sFTP(?)
2. Parse the mac-adress and date captured out of the .pcap/.cap files. Could be automated with "folder change detection".

---

## Getting a geolocation trough mac-adresses

1. Request geolocation on wigle with the parsed mac-adress. **[API Docs](https://api.wigle.net/)**
2. If geolocation is found, which is highly likely if **[Wardriving](https://en.wikipedia.org/wiki/Wardriving)** was enabled while the Pwnagotchi was running, parse it together with the other data points.

---
    
## Question / WIP
- Which Map is easy to host can be comfortable fed with geolocations and creating mappoints with data?

---

## Issues / Final Thoughts
- onlinehashcrack's API seems not to be optimized for requesting to me. For requests there is the need of a filename, because it's designed for API uploads. Maybe webscraping and parsing HTML is suitable? Should be easy since there is no need of authorization (Just E-Mail provided when uploading).
- onlinehashcrack has a feature to export *all* WPA related information trough a csv, that is amazing. Still unsure how to make use of it because it needs a cookie which gets generated after entering your mail. Have to look into it how to automate it.

## Current Depencies
- selenium (Just a temporary solution, because it's pretty overkill for this "simple" task. [I write simple in brackets, because I couldn't get it working while only using requests.])
```
pip3 install selenium
```

- requests
```
pip3 install requests
```