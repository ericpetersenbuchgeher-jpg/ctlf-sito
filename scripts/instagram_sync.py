#!/usr/bin/env python3
"""Sincronizza gli ultimi post di @ctlfmilano dentro index.html.

Cosa fa:
  1. legge i post (più recente per primo) da una di queste fonti, in ordine:
     - Instagram API con login Instagram, se c'è la variabile IG_TOKEN
       (token long-lived dell'account ctlfmilano; lo rinnova a ogni giro);
     - l'endpoint pubblico del profilo (funziona a volte, Instagram limita);
     - altrimenti tiene il feed già salvato.
  2. scarica le immagini in assets/instagram/ (le URL del CDN Instagram scadono);
  3. scrive assets/instagram/feed.json e riscrive le card in index.html
     fra <!-- IG:START --> e <!-- IG:END -->, così il widget funziona anche
     senza JavaScript e aprendo il file in locale.

Uso:  python3 scripts/instagram_sync.py           (dalla cartella del sito)
      IG_TOKEN=... python3 scripts/instagram_sync.py
"""
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USERNAME = "ctlfmilano"
LIMIT = 12
ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = ROOT / "assets" / "instagram"
FEED = IMG_DIR / "feed.json"
INDEX = ROOT / "index.html"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")
MESI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]


def get(url, headers=None, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    return data if raw else json.loads(data)


def shortcode(permalink):
    m = re.search(r"/(?:p|reel|tv)/([A-Za-z0-9_-]+)", permalink or "")
    return m.group(1) if m else None


def from_api(token):
    try:  # allunga la vita del token (60 giorni da ora); se fallisce si va avanti
        get("https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token"
            "&access_token=" + urllib.parse.quote(token))
    except Exception as e:
        print("refresh token non riuscito:", e, file=sys.stderr)
    fields = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp"
    d = get(f"https://graph.instagram.com/me/media?fields={fields}&limit={LIMIT}"
            f"&access_token={urllib.parse.quote(token)}")
    posts = []
    for m in d.get("data", []):
        sc = shortcode(m.get("permalink"))
        img = m.get("thumbnail_url") if m.get("media_type") == "VIDEO" else m.get("media_url")
        if not (sc and img):
            continue
        posts.append({
            "id": sc, "permalink": m["permalink"], "image_url": img,
            "caption": m.get("caption") or "",
            "timestamp": m["timestamp"].replace("+0000", "+00:00"),
            "type": m.get("media_type", "IMAGE").lower(),
        })
    return posts


def from_public():
    d = get(f"https://www.instagram.com/api/v1/users/web_profile_info/?username={USERNAME}",
            {"x-ig-app-id": "936619743392459"})
    posts = []
    for e in d["data"]["user"]["edge_owner_to_timeline_media"]["edges"][:LIMIT]:
        n = e["node"]
        caps = n["edge_media_to_caption"]["edges"]
        posts.append({
            "id": n["shortcode"],
            "permalink": f"https://www.instagram.com/p/{n['shortcode']}/",
            "image_url": n.get("thumbnail_src") or n["display_url"],
            "caption": caps[0]["node"]["text"] if caps else "",
            "timestamp": datetime.fromtimestamp(n["taken_at_timestamp"], timezone.utc).isoformat(),
            "type": "video" if n.get("is_video") else
                    ("carousel_album" if n["__typename"] == "GraphSidecar" else "image"),
        })
    return posts


def download(posts, old):
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    known = {p["id"]: p for p in old}
    for p in posts:
        dest = IMG_DIR / f"{p['id']}.jpg"
        p["image"] = f"assets/instagram/{p['id']}.jpg"
        if dest.exists() and p["id"] in known:
            continue
        dest.write_bytes(get(p.pop("image_url"), raw=True))
        print("scaricata", dest.name)
    for p in posts:
        p.pop("image_url", None)
    keep = {f"{p['id']}.jpg" for p in posts}
    for f in IMG_DIR.glob("*.jpg"):
        if f.name not in keep:
            f.unlink()
            print("rimossa", f.name)


def card(p):
    when = datetime.fromisoformat(p["timestamp"])
    label = f"{when.day} {MESI[when.month - 1]} {when.year}"
    first = (p["caption"].strip().splitlines() or [""])[0]
    first = re.sub(r"\s*#\S+", "", first).strip()
    if len(first) > 110:
        first = first[:107].rsplit(" ", 1)[0] + "…"
    alt = html.escape(f"Post Instagram di CTLF del {label}" + (f": {first}" if first else ""), quote=True)
    badge = {"video": "Reel", "carousel_album": "Carosello"}.get(p.get("type"), "")
    return (
        f'      <a class="igpost" href="{html.escape(p["permalink"], quote=True)}" target="_blank" rel="noopener">\n'
        f'        <img src="{p["image"]}" alt="{alt}" width="640" height="800" loading="lazy" decoding="async">\n'
        + (f'        <span class="igpost__badge">{badge}</span>\n' if badge else "")
        + f'        <span class="igpost__meta"><time datetime="{when.date().isoformat()}">{label}</time>'
        + (f'<span class="igpost__cap">{html.escape(first)}</span>' if first else "")
        + "</span>\n      </a>"
    )


def render(posts):
    src = INDEX.read_text(encoding="utf-8")
    block = "\n".join(card(p) for p in posts)
    new, n = re.subn(r"<!-- IG:START -->.*?<!-- IG:END -->",
                     lambda m: "<!-- IG:START -->\n" + block + "\n      <!-- IG:END -->", src, flags=re.S)
    if not n:
        sys.exit("marcatori IG:START / IG:END non trovati in index.html")
    if new != src:
        INDEX.write_text(new, encoding="utf-8")
        print("index.html aggiornato")


def main():
    old = json.loads(FEED.read_text()) if FEED.exists() else []
    posts = None
    token = os.environ.get("IG_TOKEN", "").strip()
    sources = ([("API Instagram", lambda: from_api(token))] if token else []) + [("profilo pubblico", from_public)]
    for name, fn in sources:
        try:
            posts = fn()
            if posts:
                print(f"{len(posts)} post da {name}")
                break
        except Exception as e:
            print(f"{name} non disponibile: {e}", file=sys.stderr)
    if posts:
        posts.sort(key=lambda p: p["timestamp"], reverse=True)
        posts = posts[:LIMIT]
        download(posts, old)
        FEED.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        print("nessuna fonte raggiungibile: tengo il feed salvato")
        posts = old
    render(posts)


if __name__ == "__main__":
    main()
