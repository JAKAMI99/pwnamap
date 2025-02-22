# pwnamap
## A Self-hosted pwnagotchi companion map

## Beta: 0.9.0
---

## TL;DR
A self-hosted companion for your little toy "pwnagotchi" to get motivated to obtain more handshakes and learn more IT security. It puts your cracked networks on a map and features statistics for motivation.

## Screenshots
### Main Map
![Screenshot of the Main Map](/images/pwnamap_main.png)
### Database Explorer
![Screenshot of the Database Explorer](/images/pwnamap_db.png)
### Stats
![Screenshot of the stats](/images/pwnamap_stats.png)

---
## Features working
- [x] Download and parse you wpa-sec.stanev.org potfile
- [x] Download your wigle wardriving data
- [x] Stats of the total handshakes and pwned Networks
- [x] Deployable as a docker container
- [x] Receive all handshakes that get send by pwnagotochis [pwnamap plugin](https://github.com/JAKAMI99/pwnamap-plugin)
- [x] Your own little wigle API that utilizes your local DB
- [x] Import your selfcracked potfile

## Comming soon™
- [ ] Utilize the gps plugin for pwnagotchis with a GPS module
- [ ] More information about your pwnagotchi (Stats, name, last seen,... )



## Why?
I created pwnamap, because I felt that the pwnagotchi gets boring after a while, and I wanted to utilize the full potential of it.
Pwnamap is supposed to give you a better insight in the networks, you successfully cracked trough wpasec or hashcat by yourself.
Since most people (like me) run their pwnagotchi in the vanilla/basicmconfiguration, without external GPS, it is difficult to get coordinates for your cracked networks.
That's why I recommend running the war driving app from [Wigle](https://wigle.net/tools) on your phone when going out for a walk with your pwnagotchi. This way, pwnamap will know where your little pwnagotchi found his loot.


# Install

### Dockerhub  (recommended) 
```
docker pull jakami/pwnamap:latest
docker run -d -p 1337:1337 -v $HOME/.docker-data:/app/app/data/ jakami/pwnamap:latest
```
### Manual Docker Build
```
git clone https://github.com/JAKAMI99/pwnamap.git
docker build -t jakami/pwnamap:latest .
docker run -d -p 1337:1337 -v $HOME/.docker-data:/app/app/data/ jakami/pwnamap:latest
```
### Docker-Compose
```
git clone https://github.com/JAKAMI99/pwnamap.git
docker-compose build
docker-compose up
```
(modify port and volume mount to your desires)
### Manual (Raspberry Pi, Bare Metal)
```
git clone https://github.com/JAKAMI99/pwnamap.git
cd pwnamap/
python3 -m pip install -r requirements.txt
python3 run.py
```
### Available in the "Unraid" Community Apps soon™

---
## Usage

### WebUI
- Access the Webinterface.
You will be prompted to setup an user. (Use secure credentials)

- Login

- Go to the Settings and fill out your wpasec and wigle API-key and click save. Doublecheck for whitespaces.

- Head over to the tools and run click the buttons to retrieve your latest wpa-sec potfile, your latest wigle uploads and geolocate with the local db.
You can use the "geolocate with Wigle"-feature. It is really limited, more information in the Wigle API section.

- Browse the pwnamap or play around with your own local db with the "Database Explorer" and the filter it comes with (It is really fun to search for funny WIFI names you've discovered) 

- You also can check the stats of your pwnamap instance to see how many fully cracked networks you have 

- Install the [pwnamap-plugin](https://github.com/JAKAMI99/pwnamap-plugin) and setup the API-Key from the Settings on your pwnagotchis config.toml to let him/her upload his/her handshakes to your pwnamap instance (More features soon™)

### Database API

Currently the Local DB comes with a simple API, that you can use for your own purposes and other projects.
You can use curl e.g. to interact with it. The API key is your "pwnamap API Key" which you can find in the settings

Example request and response:

```
jakami@kubuntu:~$ curl -H "X-API-KEY: f68de762edeb6208c37002d6f288b17d" \
     "http://pwnamap.myhost.com:1337/api/explore?network_type=WIFI&name=WLAN-1337"

[{"accuracy":4.0,"encryption":"WPA2","id":72595,
  "latitude":51.13374269,"longitude":7.13374269,
  "name":"WLAN-1337","network_id":"f8:e0:79:af:57:eb",
  "network_type":"WIFI","signal":-91.0,"time":"2023-02-25T19:53:03.000-08:00"}]
```
You can use the following parameter for your query
| Parameter      | Input      |  Example/Options                |
|----------------|------------|---------------------------------|
| network_type   | Type       | WIFI/BT/BLE/GSM/LTE             |
| network_id     | BSSID/MAC  | f8:e0:79:af:57:eb               |
| name           | SSID/Name  | Guest14                         |
| encryption     | encryption | WEP/WPA/WPA2/WPA3/None          |
| exclude_no_ssid| Filter out nameless networks | True / False  |


## Wigle API
When geolocate with the Wigle API, you are likely to run into the API Limit really fast.
New wigle users report they have less than 10 queries a day, even tho you can request an increase of your daily limit, I recommend to build your own database by wardriving and retrieving your uploads from wigle, which are not limited and only use the wigle API as a second choice.
This way you start to build up your own indepent Database which you can later user for other projects (Pwnamap includes a simple API you can utilize if you want)
### Information: 
When adding your API Token to pwnamap, make sure to use the "Encoded for use" API Token and not the Token itself, otherwise you will get blocked by the API!

![Screenshot of the API Token](/images/WigleAPI.png)

### Doublecheck for whitespaces! When you copy the Encoded for use Key, you end up with whitespaces by default






## Disclaimer
This tool is intended for educational purposes only. Any illegal use is strictly prohibited. Use responsibly and in compliance with applicable laws depending on your country. I am not liable for any misuse. Think twice and apply good ethics before you act. That you want to use pwnamap leads to the conclusion, that you seem to be quiet smart, so dont do stupid things. At least be so smart to don't get caught when doing stupid things.
