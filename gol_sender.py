#!/usr/bin/env python3
"""Gift of Lights FPP plugin: the sender.

Started by scripts/postStart.sh, stopped by scripts/preStop.sh (one copy, by PID file). Takes the events the callbacks
script queued, oldest first, fills in the show name from the playing playlist (FPP's own /api/fppd/status) and POSTs
{ title, artist, show } to the website's now-playing address with the X-LightShow-Key header.

  - The site stamps an entry with the time it arrives, so a song is only worth sending while it is fresh: of several
    waiting, everything older than STALE_S except the newest is dropped; nothing older than GIVE_UP_S is sent.
  - A refused key (401) or bad request (400) is dropped and shown on the status page; no answer, 429 or 5xx is
    retried with backoff up to MAX_BACKOFF_S.
  - Every request has a timeout; the loop sleeps between looks.
"""
import json
import os
import signal
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
import gol_common as c  # noqa: E402

POLL_S = 0.5
STALE_S = 30
GIVE_UP_S = 600
MAX_BACKOFF_S = 60
POST_TIMEOUT_S = 8
FPP_URL = os.environ.get('FPP_URL', 'http://localhost')

running = True


def stop(*_):
    global running
    running = False


def playing_playlist():
    try:
        with urllib.request.urlopen(FPP_URL + '/api/fppd/status', timeout=2) as r:
            st = json.loads(r.read().decode('utf-8', 'replace'))
        return (st.get('current_playlist') or {}).get('playlist', '') or ''
    except Exception:
        return ''


def write_status(**kw):
    try:
        cur = {}
        if os.path.exists(c.STATUSFILE):
            with open(c.STATUSFILE, encoding='utf-8') as f:
                cur = json.load(f)
        cur.update(kw)
        tmp = c.STATUSFILE + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(cur, f)
        os.replace(tmp, c.STATUSFILE)
    except Exception as e:
        c.log().warning('status file: %s', e)


def post(url, key, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), method='POST', headers={
        'Content-Type': 'application/json', 'X-LightShow-Key': key, 'User-Agent': c.REPO + '/1'})
    try:
        with urllib.request.urlopen(req, timeout=POST_TIMEOUT_S) as r:
            return r.status, ''
    except urllib.error.HTTPError as e:
        return e.code, e.read(300).decode('utf-8', 'replace')
    except Exception as e:
        return 0, str(e)


def pending():
    try:
        names = sorted(n for n in os.listdir(c.QUEUE) if n.endswith('.json'))
    except OSError:
        return []
    out = []
    for n in names:
        p = os.path.join(c.QUEUE, n)
        try:
            with open(p, encoding='utf-8') as f:
                out.append((p, json.load(f)))
        except (OSError, ValueError):
            _rm(p)
    return out


def _rm(p):
    try:
        os.remove(p)
    except OSError:
        pass


def body_of(ev, cfg):
    if ev.get('stop'):
        return {'title': '', 'artist': '', 'show': ''}
    show = ev.get('show') or c.show_name(playing_playlist(), cfg)
    return {'title': ev.get('title', ''), 'artist': ev.get('artist', ''), 'show': show}


def once(state):
    """One pass over the queue. Returns seconds to sleep."""
    items = pending()
    if not items:
        return POLL_S
    now = time.time()
    # Fresh enough to send: the newest always (unless past GIVE_UP_S), older ones only while within STALE_S.
    keep = []
    for i, (p, ev) in enumerate(items):
        age = now - ev.get('queuedAt', now)
        newest = i == len(items) - 1
        if age > GIVE_UP_S or (not newest and age > STALE_S):
            c.log().info('dropped (too old to show): %s', ev.get('title') or '(stop)')
            _rm(p)
        else:
            keep.append((p, ev))
    if not keep:
        return POLL_S
    cfg = c.settings()
    url, key = (cfg.get('BackendUrl') or '').strip(), c.key()
    if not url.startswith('https://') or len(key) < 16:
        write_status(lastError='Set the website address (https) and the key on the plugin page.', lastErrorAt=now)
        return 5
    p, ev = keep[0]
    body = body_of(ev, cfg)
    code, text = post(url, key, body)
    if 200 <= code < 300:
        _rm(p)
        state['backoff'] = 0
        c.log().info('sent: %s / %s / %s', body['title'] or '(nothing playing)', body['artist'], body['show'])
        write_status(lastSent=body, lastSentAt=time.time(), lastError='', lastErrorAt=0)
        return 0
    if code in (400, 401, 403, 404):
        _rm(p)
        msg = {401: 'The website refused the key - it must match LIGHTSHOW_FEED_KEY.',
               404: 'The website address is wrong (404).'}.get(code, 'The website refused the post (%d).' % code)
        c.log().warning('%s %s', msg, text[:200])
        write_status(lastError=msg, lastErrorAt=time.time())
        return 0
    state['backoff'] = min(MAX_BACKOFF_S, max(2, state.get('backoff', 0) * 2))
    msg = ('No answer from the website: %s' % text) if code == 0 else ('The website answered %d; trying again.' % code)
    if code == 503 and 'LIGHTSHOW_FEED_KEY' in text:
        msg = 'The website has no LIGHTSHOW_FEED_KEY set yet; trying again.'
    c.log().warning('%s (retry in %ss)', msg, state['backoff'])
    write_status(lastError=msg, lastErrorAt=time.time())
    return state['backoff']


def main():
    os.makedirs(c.QUEUE, exist_ok=True)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    with open(c.PIDFILE, 'w') as f:
        f.write(str(os.getpid()))
    c.log().info('sender started')
    state = {}
    try:
        while running:
            try:
                wait = once(state)
            except Exception as e:
                c.log().error('sender: %s', e)
                wait = 5
            end = time.time() + wait
            while running and time.time() < end:
                time.sleep(min(POLL_S, max(0.05, end - time.time())))
    finally:
        try:
            with open(c.PIDFILE) as f:
                if f.read().strip() == str(os.getpid()):
                    os.remove(c.PIDFILE)
        except OSError:
            pass
        c.log().info('sender stopped')


if __name__ == '__main__':
    main()
