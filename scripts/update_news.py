#!/usr/bin/env python3
"""Obtiene titulares públicos de Google News RSS y los guarda como JSON estático."""
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

FEEDS = [
    ("Google News · GTA VI", "https://news.google.com/rss/search?q=GTA+VI+when:7d&hl=es&gl=ES&ceid=ES:es"),
    ("Google News · Rockstar Games", "https://news.google.com/rss/search?q=Rockstar+Games+GTA+6&hl=es&gl=ES&ceid=ES:es"),
]
def clean(value):
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", unescape(value)).strip()
items, seen = [], set()
for source, url in FEEDS:
    req = urllib.request.Request(url, headers={"User-Agent": "RadarViceCity/1.0 (news aggregator)"})
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            root = ET.fromstring(response.read())
        for item in root.findall(".//item"):
            title = clean(item.findtext("title"))
            link = (item.findtext("link") or "").strip()
            description = clean(item.findtext("description"))
            if not title or not link or link in seen:
                continue
            seen.add(link)
            date_raw = item.findtext("pubDate") or ""
            try:
                date = parsedate_to_datetime(date_raw).astimezone(timezone.utc).isoformat()
            except Exception:
                date = None
            items.append({"title": title, "link": link, "description": description[:320],
                          "source": source, "date": date})
    except Exception as exc:
        print(f"No se pudo leer {source}: {exc}")
items.sort(key=lambda x: x.get("date") or "", reverse=True)
payload = {"updated": datetime.now(timezone.utc).isoformat(), "items": items[:30]}
out = Path("data/news.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Guardadas {len(payload['items'])} noticias.")
