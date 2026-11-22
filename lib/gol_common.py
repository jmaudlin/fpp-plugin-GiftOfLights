"""Gift of Lights FPP plugin: what the callbacks script and the sender share.

Paths follow FPP's plugin rules: settings in config/plugin.<repo> (written by the settings page through
WriteSettingToFile), the key and the queue in plugindata/<repo>/ (secrets never go in config/), one log at
<logdir>/plugin-<repo>.log reopened after FPP rotates it.
"""
import json
import logging
import logging.handlers
import os
import re
import time

REPO = 'fpp-plugin-GiftOfLights'
MEDIADIR = os.environ.get('MEDIADIR', '/home/fpp/media')
CFGDIR = os.environ.get('CFGDIR', os.path.join(MEDIADIR, 'config'))
LOGDIR = os.environ.get('LOGDIR', os.path.join(MEDIADIR, 'logs'))
DATADIR = os.path.join(MEDIADIR, 'plugindata', REPO)
QUEUE = os.path.join(DATADIR, 'queue')
KEYFILE = os.path.join(DATADIR, 'key')
STATUSFILE = os.path.join(DATADIR, 'status.json')
PIDFILE = os.path.join(DATADIR, 'sender.pid')
CFGFILE = os.path.join(CFGDIR, 'plugin.' + REPO)
TEXT_MAX = 120

_log = None


def log():
    global _log
    if _log is None:
        _log = logging.getLogger(REPO)
        _log.setLevel(logging.INFO)
        try:
            h = logging.handlers.WatchedFileHandler(os.path.join(LOGDIR, 'plugin-' + REPO + '.log'))
            h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
            _log.addHandler(h)
        except OSError:
            _log.addHandler(logging.NullHandler())
    return _log


def settings():
    """config/plugin.<repo>: lines of  key = "value"."""
    out = {}
    try:
        with open(CFGFILE, encoding='utf-8') as f:
            for line in f:
                m = re.match(r'\s*([A-Za-z0-9_]+)\s*=\s*"?(.*?)"?\s*$', line)
                if m:
                    out[m.group(1)] = m.group(2)
    except OSError:
        pass
    return out


def key():
    try:
        with open(KEYFILE, encoding='utf-8') as f:
            return f.read().strip()
    except OSError:
        return ''


def clip(s, n=TEXT_MAX):
    t = re.sub(r'\s+', ' ', str(s or '')).strip()
    return t[:n]


def tidy(name):
    """A media or sequence file name as a title: no folder, extension or leading track number."""
    base = os.path.basename(str(name or ''))
    base = re.sub(r'\.[A-Za-z0-9]{2,4}$', '', base)
    base = re.sub(r'^\d+[\s._-]+', '', base)
    return re.sub(r'_+', ' ', base).strip()


def show_name(playlist, cfg=None):
    """The playlist name as it should read on the site (Show names setting: one 'playlist = name' per line,
    stored with | between lines)."""
    cfg = cfg if cfg is not None else settings()
    for line in (cfg.get('ShowNames') or '').split('|'):
        if '=' in line:
            a, b = line.split('=', 1)
            if a.strip().lower() == str(playlist or '').strip().lower():
                return clip(b, 80)
    return clip(playlist, 80)


def enqueue(event):
    """Hand one event to the sender and return at once (the callback must never make fppd wait).
    Written to a temp name and renamed, so the sender never reads half a file."""
    os.makedirs(QUEUE, exist_ok=True)
    event = dict(event, queuedAt=time.time())
    name = '%020d-%d' % (time.time_ns(), os.getpid())
    tmp = os.path.join(QUEUE, '.' + name)
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(event, f)
    os.replace(tmp, os.path.join(QUEUE, name + '.json'))
