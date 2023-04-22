# Automated Pwnagotchi Handshake Map

---

## Idea
A selfhosted(!) map which shows all captured handshakes and highlights those which are successfully got cracked. (red/green POIs)

---

## Workflow
1. Autoupload caputured handshakes to onlinehashcrack **[Plugin](https://github.com/evilsocket/pwnagotchi/blob/master/pwnagotchi/plugins/default/onlinehashcrack.py)**
    1. Upload pcap files to the server
    2. Get *autouploaded* handshake and cracked passwords from 
    onlinehashcrack **[API Docs](https://api.onlinehashcrack.com/)**

2. Parser searches for new files every x minutes and parses the mac-adress

3. Webserver requests geolocation on wigle with the parsed mac-adress **[API Docs](https://api.wigle.net/)**

4. If geolocation is found (is highly likely if war driving was enabled Pwnagotchi was running) parse it together with the following data on the map:
    1. E-SSID
    2. B-SSID
    3. (?) Found password
    4. Time captured
    5. (?) maybe geocoded adress
    
## Question / WIP
- Which Map is easy to host can be comfortable fed with geolocations and creating mappoints with data?

## Issues / Final Thoughts
- onlinehashcrack's API is not optimized for requesting. For requests there is the need of a filename, because it's designed for API uploads. Maybe parsing the raw HTML is suitable? Should be easy since there is no need of authorization (Just E-Mail provided when uploading).