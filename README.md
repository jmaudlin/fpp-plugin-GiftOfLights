# Gift of Lights - Now Playing (FPP plugin)

Runs on the show's Falcon Player (FPP). As each song starts it sends `{ title, artist, show }` to the website's
`POST /api/lightshow/now-playing` (backend README -> Light show stream), with the header `X-LightShow-Key`, so the
Gift of Lights page can show what is playing. The site shows it only while the stream is on air.

## What it sends

- **Title and artist**: the song's own tags, which fppd reads and hands to the plugin. A song with no tags shows its
  file name, tidied (no folder, extension or leading track number).
- **Show**: the name of the playlist that is playing, or the name given to it under Show names on the plugin page.
- **A sequence on its own** (no audio): its sequence name as the title.
- **Playlist stopped**: a blank title, so the site stops showing the last song.

## How it works

- `callbacks.py` - fppd runs it as each song starts (`media`) and as playlists start, move on and stop (`playlist`).
  fppd waits for it, so it only writes the event to `plugindata/fpp-plugin-GiftOfLights/queue/` and returns.
- `gol_sender.py` - started with fppd (`scripts/postStart.sh`, and once at install), stopped with it
  (`scripts/preStop.sh`). It posts the queued events oldest first. Because the site stamps each one with the time it
  arrives, an event that waited more than 30 s behind a newer one is dropped, and nothing older than 10 minutes is sent.
  A refused key (401) or bad request is dropped and shown on the plugin page; no answer, 429 or 5xx is retried, backing
  off to a minute.
- `content.php` + `js/gol.js` + `api.php` - the plugin's page under **Content Setup -> Gift of Lights - Now Playing**:
  the on/off switch, the website address, the key, show names, a Send a test song button and the sender's last post
  or problem.
- Settings live in `config/plugin.fpp-plugin-GiftOfLights`; the key lives in `plugindata/fpp-plugin-GiftOfLights/key`
  (mode 600), never in `config/`. The log is `logs/plugin-fpp-plugin-GiftOfLights.log` (FPP rotates it).
- Python standard library only; nothing is downloaded.

## Install

1. In FPP: Content Setup -> Plugin Manager, paste
   `https://raw.githubusercontent.com/jmaudlin/fpp-plugin-GiftOfLights/main/pluginInfo.json` into the plugin info
   box, Retrieve Plugin Info, then Install.
2. Content Setup -> Gift of Lights - Now Playing: the website address
   (`https://mahaskadrug-photos.azurewebsites.net/api/lightshow/now-playing`), the key (the website's
   `LIGHTSHOW_FEED_KEY`), switch it on, Save, then Send a test song. Last sent should show the test within seconds.

The source of record is `tools/fpp-plugin-GiftOfLights/` in the MahaskaDrugShopify repository; this repository is
what FPP installs from, kept the same.

Uninstall (Plugin Manager, or `scripts/fpp_uninstall.sh`) stops the sender and removes the plugin's settings, key and
queue.
