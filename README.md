# Automated Pwnagotchi Handshake Map

---

## Idea
A selfhosted(!) map which shows all captured handshakes and highlights those which are successfully got cracked. (red/green POIs)

---

## Workflow getting data
There are two different ideas of data retrieval. 
### Fully "automatic" but third-party-dependent way:

1. Autoupload caputured handshakes to onlinehashcrack with the pwnagotchi **[Plugin](https://github.com/evilsocket/pwnagotchi/blob/master/pwnagotchi/plugins/default/onlinehashcrack.py)**
2. Get *auto-uploaded* handshakes and cracked passwords from onlinehashcrack. There is an API available, not sure if suitable for requesting **[API Docs](https://api.onlinehashcrack.com/)**
3. Parse the mac-adress out of the API-request together with the BSSID, AP-Vendor, Date added and if found the cracked password.

### Manual uploading
1. Manually upload the handshakes to the webserver trough eg. sFTP(?)
2. Parse the mac-adress and date captured out of the .pcap/.cap files. Could be automated with "folder change detection".

## Getting a geolocation trough mac-adresses

1. Request geolocation on wigle with the parsed mac-adress. **[API Docs](https://api.wigle.net/)**
2. If geolocation is found, which is highly likely if **[Wardriving](https://en.wikipedia.org/wiki/Wardriving)** was enabled while the Pwnagotchi was running, parse it together with the other data points.
    
## Question / WIP
- Which Map is easy to host can be comfortable fed with geolocations and creating mappoints with data?

## Issues / Final Thoughts
- onlinehashcrack's API is not optimized for requesting. For requests there is the need of a filename, because it's designed for API uploads. Maybe parsing the raw HTML is suitable? Should be easy since there is no need of authorization (Just E-Mail provided when uploading).