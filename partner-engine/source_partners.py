#!/usr/bin/env python3
"""Partner sourcing: find and rank creators/agencies who fit Blotato.

Two input modes:
  1. --youtube "n8n automation" "faceless content"   (needs YOUTUBE_API_KEY; pulls
     channels from the YouTube Data API v3 search + channels endpoints)
  2. --csv data/sample_candidates.csv               (any scraped list: YouTube, TikTok,
     agency directories, X lists, newsletter directories)

Every candidate gets a 0-100 fit score and a drafted first line for outreach,
then lands in out/partner_leads.csv, sorted best-first. Standard library only.

Scoring (tuned for "will this partner refer 10 customers a month?"):
  topic fit      45  - talks about AI, automation, content systems, social media ops
  audience band  25  - 5k-250k followers: big enough to convert, small enough to reply
  consistency    15  - posting at least weekly
  reachable      10  - business email / site found
  agency bonus    5  - agencies resell to many clients at once
"""
import argparse
import csv
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
TOPICS = {
    "automation": 9, "automate": 9, "n8n": 9, "make.com": 7, "zapier": 7, " ai ": 6, "chatgpt": 5,
    "claude": 6, "agent": 6, "content system": 8, "repurpos": 8, "schedul": 7, "faceless": 7,
    "social media": 8, "creator": 5, "agency": 6, "solopreneur": 6, "workflow": 6, "no-code": 6,
}
NEGATIVE = {"meme": -15, "gadget": -8, "news": -6, "gaming": -10}


def topic_score(text):
    t = f" {text.lower()} "
    s = sum(w for k, w in TOPICS.items() if k in t) + sum(w for k, w in NEGATIVE.items() if k in t)
    return max(0, min(45, s))


def audience_score(f, platform):
    if platform == "web":
        return 15  # agencies: the audience is their client list
    if 5_000 <= f <= 250_000:
        return 25
    if 1_000 <= f < 5_000 or 250_000 < f <= 1_000_000:
        return 12
    return 4


def score(c):
    plat = c.get("platform", "")
    posts = int(c.get("posts_last_30d") or 0)
    s = topic_score(c.get("bio", "") + " " + c.get("name", ""))
    s += audience_score(int(c.get("followers") or 0), plat)
    s += 10 if plat == "web" else 15 if posts >= 4 else 8 if posts >= 2 else 0
    s += 10 if str(c.get("has_business_email", "")).lower() in ("yes", "true", "1") else 0
    s += 5 if plat == "web" and "agency" in c.get("bio", "").lower() else 0
    return min(100, s)


OPENERS = {
    "n8n": "your n8n builds are exactly the workflows Blotato's API and MCP server plug into.",
    "faceless": "faceless channels live and die by posting volume, which is what Blotato automates.",
    "repurpos": "your repurposing workflow is basically a Blotato demo waiting to happen.",
    "schedul": "you already teach scheduling, and Blotato does it across 11 platforms from one API.",
    "agency": "agencies running many client accounts get the most out of one posting API.",
    "automation": "your audience wants automations that ship content, and that's Blotato's whole job.",
    "content": "your audience is building content systems, which is where Blotato fits.",
}


def opener(c):
    bio = c.get("bio", "").lower()
    hook = next((k for k in OPENERS if k in bio), "content")
    return f"Hi {c.get('name', 'there').split()[0]}, {OPENERS[hook]}"


def from_youtube(queries, key, per_query=15):
    base = "https://www.googleapis.com/youtube/v3/"
    ids = []
    for q in queries:
        p = urllib.parse.urlencode({"part": "snippet", "q": q, "type": "channel",
                                    "maxResults": per_query, "key": key})
        data = json.load(urllib.request.urlopen(base + "search?" + p, timeout=20))
        ids += [i["snippet"]["channelId"] for i in data.get("items", [])]
    out = []
    for i in range(0, len(ids), 50):
        p = urllib.parse.urlencode({"part": "snippet,statistics", "id": ",".join(ids[i:i + 50]), "key": key})
        data = json.load(urllib.request.urlopen(base + "channels?" + p, timeout=20))
        for ch in data.get("items", []):
            desc = ch["snippet"].get("description", "")
            out.append({
                "name": ch["snippet"]["title"], "platform": "youtube",
                "url": f"https://youtube.com/channel/{ch['id']}",
                "followers": ch["statistics"].get("subscriberCount", 0),
                "posts_last_30d": "",  # fill from the activities endpoint if needed
                "bio": desc[:300],
                "has_business_email": "yes" if re.search(r"[\w.+-]+@[\w-]+\.\w+", desc) else "no",
            })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="CSV of scraped candidates")
    ap.add_argument("--youtube", nargs="*", help="search queries (needs YOUTUBE_API_KEY)")
    ap.add_argument("--min-score", type=int, default=50)
    a = ap.parse_args()

    if a.youtube:
        key = os.environ.get("YOUTUBE_API_KEY")
        if not key:
            raise SystemExit("Set YOUTUBE_API_KEY to search YouTube.")
        cands = from_youtube(a.youtube, key)
    else:
        with open(a.csv or HERE / "data/sample_candidates.csv", newline="", encoding="utf-8") as f:
            cands = list(csv.DictReader(f))

    seen, leads = set(), []
    for c in cands:
        if c["url"] in seen:
            continue
        seen.add(c["url"])
        c["fit_score"], c["opener"] = score(c), opener(c)
        leads.append(c)
    leads.sort(key=lambda c: -c["fit_score"])

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    cols = ["fit_score", "name", "platform", "url", "followers", "has_business_email", "opener"]
    with open(out / "partner_leads.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(leads)

    keep = sum(c["fit_score"] >= a.min_score for c in leads)
    print(f"{len(leads)} candidates scored, {keep} at or above {a.min_score}:\n")
    for c in leads:
        mark = "KEEP" if c["fit_score"] >= a.min_score else "skip"
        print(f"  [{mark}] {c['fit_score']:>3}  {c['name']}  ({c['platform']})")


if __name__ == "__main__":
    main()
