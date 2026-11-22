#!/usr/bin/env python3
"""Gift of Lights FPP plugin: fppd's callbacks.

fppd runs this with --list once at start, then --type media --data <json> as each song starts and
--type playlist --data <json> as playlists start, move on and stop. fppd waits for this script to exit,
so all it does is write the event to the queue and return; gol_sender.py posts it.

  media      title / artist from the song's tags (fppd reads them), else the file name tidied up
  playlist   an item with no media (a sequence on its own) sends the sequence name as the title;
             "stop" sends a blank title so the site stops showing the last song
The show name is filled in by the sender from the playing playlist.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
import gol_common as c  # noqa: E402


def arg(name):
    a = sys.argv
    return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else ''


def main():
    if '--list' in sys.argv:
        print('media,playlist')
        return 0
    kind = arg('--type')
    try:
        data = json.loads(arg('--data') or '{}')
    except ValueError:
        return 0
    if c.settings().get('Enabled', '1') == '0':
        return 0
    if kind == 'media':
        title = data.get('title') or c.tidy(data.get('Media') or data.get('Sequence'))
        c.enqueue({'title': c.clip(title), 'artist': c.clip(data.get('artist'))})
    elif kind == 'playlist':
        action = data.get('Action', '')
        entry = data.get('currentEntry') or {}
        if action == 'stop':
            c.enqueue({'title': '', 'artist': '', 'stop': True})
        elif action == 'playing' and entry.get('type') == 'sequence':
            c.enqueue({'title': c.clip(c.tidy(entry.get('sequenceName'))), 'artist': '', 'show': c.show_name(data.get('name'))})
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:  # a callback must never fail fppd's playlist
        try:
            c.log().error('callback: %s', e)
        except Exception:
            pass
        sys.exit(0)
