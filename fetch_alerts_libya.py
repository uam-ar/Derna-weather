#!/usr/bin/env python3
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# Official WMO register CAP RSS (Arabic)
LIBYA_CAP_RSS = "https://cap-sources.s3.amazonaws.com/ly-nmc-ar/rss.xml"

def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "darna-weather (CAP alerts fetcher)"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")

def strip_tags(s: str) -> str:
    # Simple HTML tag remover
    out = []
    in_tag = False
    for ch in s or "":
        if ch == "<":
            in_tag = True
            continue
        if ch == ">":
            in_tag = False
            continue
        if not in_tag:
            out.append(ch)
    return " ".join("".join(out).split())

def main():
    xml_text = fetch_text(LIBYA_CAP_RSS)
    root = ET.fromstring(xml_text)

    # RSS structure: channel/item
    channel = root.find("channel")
    items = channel.findall("item") if channel is not None else []

    alerts = []
    for it in items[:5]:
        title = (it.findtext("title") or "تنبيه").strip()
        pub = (it.findtext("pubDate") or "").strip()
        desc = (it.findtext("description") or "").strip()

        alerts.append({
            "title": title,
            "published": pub,
            "summary": strip_tags(desc),
        })

    out = {
        "meta": {
            "source": "WMO CAP (Libyan National Meteorological Centre)",
            "feed": LIBYA_CAP_RSS,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
        },
        "alerts": alerts
    }

    with open("alerts.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("Wrote alerts.json")

if __name__ == "__main__":
    main()
