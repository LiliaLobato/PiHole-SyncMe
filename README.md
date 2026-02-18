# [PiHole SyncMe](#pihole-syncme) + [Digital Detox](#extra-setup) + [Smart Devices Data Tracking](#dont-forget-your-tv-your-fridge-your-doorbell-your-lightbulbs-your-smart-photo-frames)

I will be updating as I discover new tools after adoption and testing. 
<div style="text-align: center;">
<img src="images/signsTinFoilHat.jpg" alt="Signs tin foil hat scene" width="500"/>
</div>

<br><br>

# PiHole SyncMe
[Pi-hole](https://en.wikipedia.org/wiki/Pi-hole) is a Linux network-level advertisement and Internet tracker blocking application which acts as a DNS sinkhole and optionally a DHCP server, intended for use on a private network.
<br>Im hosting a simple block and allow list to feed my PiHole, dont use the .txt for your setup. I will be adding whatever I need and can/may/will block/unblock things you dont want.

**This is not a tutorial but** :eyes: **I will leave some information for you to follow.** <mark style="background: #8ddadaa6;">Once your data is out there, you no longer have control over it.</mark>

## Hardware
- Raspberry Pi Zero 2 W
- 32GB SD card

    ### Optional:
    My internet provideer router has a lot of configurations blocked
    - GL-iNet Travel Router

## How to setup your PiHole
- [Official PiHole documentation](https://pi-hole.net/)
- [The World’s Greatest Pi-hole (and Unbound) Tutorial 2023](https://www.crosstalksolutions.com/the-worlds-greatest-pi-hole-and-unbound-tutorial-2023)
- [Give your SD card a break with logs2ram](https://github.com/azlux/log2ram)
- [Commonly Whitelisted Domains](https://discourse.pi-hole.net/t/commonly-whitelisted-domains/212)
- Do a backup copy of your PiHole setup on a new SD card and document your network. Dont learn the hard way.
- [r/pihole](https://www.reddit.com/r/pihole/)

## What pubic blocklist do I consume?
Do you own research before adding anything to your setup and remember to periodically update Gravity.

<details open> <summary>Base</summary>

- https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts 

</details>

<details> <summary>Tracking & Telemetry Lists</summary>

- https://v.firebog.net/hosts/Easyprivacy.txt
- https://v.firebog.net/hosts/Prigent-Ads.txt
- https://perflyst.github.io/PiHoleBlocklist/SessionReplay.txt
- https://perflyst.github.io/PiHoleBlocklist/android-tracking.txt
- https://raw.githubusercontent.com/crazy-max/WindowsSpyBlocker/master/data/hosts/spy.txt
- https://raw.githubusercontent.com/ReverseTelnet/PiHoleBlockList/refs/heads/master/netflix-trackers.txt // My TV was pinging netflix... I dont have a netflix account logged in, why you need my data?!
- https://raw.githubusercontent.com/Isaaker/Spotify-AdsList/main/Lists/pi-hole.txt // Disclaimer: I pay for the service, this blocks trackers and needs a some whitelisting
- https://raw.githubusercontent.com/nickspaargaren/no-amazon/refs/heads/master/amazon.txt // Bye bye Amazon, needs some whitelisting for day to day use

</details>

<details> <summary>Smart Tv trackers</summary>

- https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt
- https://perflyst.github.io/PiHoleBlocklist/AmazonFireTV.txt // Needs some whitelisting to not block boot sequence
- https://raw.githubusercontent.com/nocturnalarchives/BlockLists/refs/heads/master/amazon-firestick-updates.txt

</details>

<details> <summary>Advertising Lists</summary>

- https://adaway.org/hosts.txt
- https://v.firebog.net/hosts/AdguardDNS.txt

</details>

<details> <summary>AntiMalware & Spam</summary>

- https://raw.githubusercontent.com/PolishFiltersTeam/KADhosts/master/KADhosts.txt
- https://raw.githubusercontent.com/FadeMind/hosts.extras/master/add.Spam/hosts
- https://raw.githubusercontent.com/DandelionSprout/adfilt/master/Alternate%20versions%20Anti-Malware%20List/AntiMalwareHosts.txt
- https://v.firebog.net/hosts/Prigent-Crypto.txt
- https://raw.githubusercontent.com/anudeepND/blacklist/master/CoinMiner.txt

</details>

<details> <summary>Phishing</summary>

- https://phishing.army/download/phishing_army_blocklist_extended.txt
- https://raw.githubusercontent.com/StevenBlack/hosts/master/alternates/fakenews/hosts
- http://sbc.io/hosts/alternates/gambling-only/hosts

</details>

<details> <summary>AI</summary>

- https://raw.githubusercontent.com/laylavish/uBlockOrigin-HUGE-AI-Blocklist/main/noai_hosts.txt

</details>

## Test your setup
Just go into any ad/tracker heavy page, 
- [Quick non invasive test 1 (speedtes.com)](https://www.speedtest.net/)
- [Quick non invasive test 2 (cnet.com)](https://www.cnet.com/)
- [Simple page to test if your PiHole setup is working - test 3](https://fuzzthepiguy.tech/adtest/)
- [Dam... dont click anything from here if you see them](https://canyoublockit.com/)

It should look like this:
<div style="text-align: center;">
<img src="images/fuzzThePiGuy.png" alt="PiHole test passing the visual inspection on an ad/tracker heavy page" width="600"/>
<figcaption><br>You dont have your PiHole setup yet? Try test 3 and see the difference. :skull: </figcaption>
</div>

If you see them, something is wrong. It could be a dns leak somewhere in your network:
- [DNS leak test](https://www.dnsleaktest.com/)

Or you just need better lists:
- [The Big Blocklist Collection](https://firebog.net/)

<br><br>

# Extra setup
I been in a digital detox journey, this are cool things to add to your setup!

## Browser and search engine
<mark style="background: #8ddadaa6;">If you dont wanna do the big browser jump:<mark> just switch your search engine to [DuckDuckGo](https://duckduckgo.com/)

Both browser options are avilable for web and mobile and do your own research. 
I run 2 browsers: DuckDuckGo and Firefox.
- **DuckDuckGo** is my default browser, its privacy focused and does not collect data. 
    - You can opt out of targeted ads and you can moderate or eliminate its AI products. **Bye Bye AI summary during search!**
    - The results feel more organic, less AI dead pages. If you dont like the results try [relearning how to search without tracking](https://thedroidguy.com/solutions-for-irrelevant-duckduckgo-search-results-what-to-do-1266007) and [Tips & Tricks to Get Search Engines to Return Authentic Results](https://github.com/laylavish/TipsTricksGoogleSearch)
    - It not chromium based so there are no extensions.
- **Firefox** is my app replacement browser. Yes, access them here instead of the mobile app.
    - Once you setup your PiHole you will notice that some websites run ad/trackers from the same domain as its content (coff coff Reddit). This behaivior is even more prevalent on apps but we can sometimes go around it by accessing them via a browser (coff coff Pinterest). <br>
    This is setup my extension setup:
        - [DuckDuckGo Search & Tracker Protection](https://chromewebstore.google.com/detail/duckduckgo-search-tracker/bkdgflcldnnnapblkhphbgpggdiikppg)
        - [AdBlock](https://chromewebstore.google.com/detail/adblock-bloquea-anuncios/gighmmpiobklfepjocnamgkkbiglidom)
        - [Blocktube](#blocktube)
        - [UnTrap](#untrap)

## Youtube (Blocktube & UnTrap)
### Blocktube
Have you ever search "music to study" on youtube in the past 6 months? Most of the music is AI generated :dizzy_face: and im tired of it.
<br> This lead me to a [sarasshu](https://surasshu.com/blocklist-for-ai-music-on-youtube/) a composer/producer with a blog sharing Blocktube and an initial block list full of AI music chanels.

<div style="text-align: center;">
<img src="https://surasshu.com/wp-content/uploads/2025/01/image-2-1024x544.png" alt="Screenshot of youtube showing a playlist of AI music (& with AI art), and all but one recommended video is also AI generated. Author: sarasshu" width="500"/>
<figcaption><br>Screenshot of youtube showing a playlist of AI music (& with AI art), and all but one recommended video is also AI generated. Image Author: sarasshu</figcaption>
</div>

- Extension: [Blocktube](https://chromewebstore.google.com/detail/blocktube/bbeaicapbccfllodepmimpkgecanonai)
- Repo: [amitbl/blocktube · GitHub](https://github.com/amitbl/blocktube/)
- Basic block list: [blocklist for AI music on youtube – surasshu](https://surasshu.com/blocktube_backup--AI%20music%20blocklist--updated%20August%202025.json)

### UnTrap
Im trying to consume less short term content and be mindfull of my mindless scrolling.<br>
<mark style="background: #8ddadaa6;">If you are not ready for the big youtube in browser jump:</mark> install [ScreenZen](https://screenzen.co/) to block youtube shorts on the app.
- For your browser, checkout [UnTrap](https://untrap.app/), it allows you to disable shorts, infinite scroll and personalize the layout.
- Extension: [UnTrap](https://chromewebstore.google.com/detail/untrap-%E2%80%93-eliminar-youtube/enboaomnljigfhfjfoalacienlhjlfil)

<br><br>

# Dont forget your TV, your fridge, your doorbell, your lightbulbs, your smart photo frames...
Your **Smart TV uses [Automatic Content Recognition (ARC)](https://en.wikipedia.org/wiki/Automatic_content_recognition) technology**  to identify content playing and serve you advertising and customized content. Do you remember [Shazam](https://www.shazam.com/)? That is ARC (audio only)

Your TV captures the video and audio snippets from TV programming, streaming content, and even external sources connected through HDMI ports, such as gaming consoles or laptops and uses [fingerprinting](https://en.wikipedia.org/wiki/Fingerprint_(computing)) and [watermarking](https://en.wikipedia.org/wiki/Digital_watermarking) to create an unique identifier. The content is compared with a database of known recorded works; if there is a match, ARC returns the corresponding metadata regarding the media as well as other associated or recommended content back to the client application for display to the user. 

NO, its not sending screenshots... but I dont like having my own free time surveyed and sold.

 Your **Smart Consumer devices** help grow and maintain your personal profile that is later used in [real-time bidding (RTB)](https://en.wikipedia.org/wiki/Real-time_bidding), a means by which advertising inventory is bought and sold on a per-impression basis. 


More information:
- [Yes, Your TV Is Probably Spying on You. Your Fridge, Too. Here’s What They Know. -NYT Wirecutter](https://www.nytimes.com/wirecutter/reviews/advice-smart-devices-data-tracking/)
- [FTC Order Prohibits Data Broker X-Mode Social and Outlogic from Selling Sensitive Location Data -FTC](https://www.ftc.gov/news-events/news/press-releases/2024/01/ftc-order-prohibits-data-broker-x-mode-social-outlogic-selling-sensitive-location-data)
- [VIZIO to Pay $2.2 Million to FTC, State of New Jersey to Settle Charges It Collected Viewing Histories on 11 Million Smart Televisions without Users’ Consent -FTC](https://www.ftc.gov/news-events/news/press-releases/2017/02/vizio-pay-22-million-ftc-state-new-jersey-settle-charges-it-collected-viewing-histories-11-million)


## What can I do?
<mark style="background: #8ddadaa6;">Non negotiable:</mark>
- Go to the configuration, navigate to the Privacy or Data Collection sections and opt out of anything you can.
- Opt out of personalized advertising and data sharing agreements in the privacy menu.
- Turn off voice recognition or voice control features. Specially if you do not use them.

Setup network level protecton:
- Connect your devices to your PiHole setup (This is why a stand alone adBlocker on your browser is not enough.) or setup another blocking service (AdGuard maybe) in your router.
- Some [devices have hardcoded DNS](https://github.com/buckmelanoma/hardcoded-dns-list/blob/master/list.csv) to avoid DNS based blocking: Google cast, Google Home, Amazon Alexa, Vizio TVs, Google Pixel, Netflix on Android, Roku, Ring Doorbell, etc. You need to  redirect any port 53 packets to the pihole but some device will simply refuse to work... pick your battles and keep it in mind when buying your products.
    - Your router setup will be different but you can use this as a guide: [Redirect Hard-coded DNS To Pi-hole Using Ubiquiti EdgeRouter](https://www.derekseaman.com/2019/10/redirect-hard-coded-dns-to-pi-hole-using-ubiquiti-edgerouter.html)

Skip the default launcher:
- If you have an Android TV, change the default launcher to [Projectivy Launcher](https://play.google.com/store/apps/details?id=com.spocky.projengmenu&hl=en-US) or sideload it. <br>
Note: This does absolutely nothing for privacy or blocking, it just takes out the big distracting launcher.




<br><br>
---
# Have fun! Be safe! Touch grass!
![Teddy bear infront of a mountain](images/TouchGrass.jpg)