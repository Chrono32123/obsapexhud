# obsapexhud

An obspython script that pulls Apex Legends Ranked stats from Tracker.gg into your obs overlays

This script is meant mostly just to see if I could do it but I learned a lot about obs scripting and it could be useful to port this setup to other games that have api support.

I borrowed from [obspokemonhud](https://github.com/guitaristtom/obspokemonhud) HEAVILY so shoutout to them for the inspiration.

OBS SETUP:

0. Download/clone this entire repo to your machine and extract where desired.
1. You will need to create two Image and two Text sources.
2. Import 'get-apex-stats.py' into the Scripts section of OBS
3. Select your platform (xbl, psn, or origin). NOTE: Tracker.gg doesn't show switch at this time.
4. Enter your gamertag for your selected platform.
5. Enter your api-key for tracker.gg (Go to https://tracker.gg/developers/docs/getting-started to sign up and generate your api-key)
6. Select your created image and text sources from the Ranked Image, Ranked Value, Arenas Ranked Image, and Arenas Ranked Value

KNOWN ISSUES:

None that I know of?
