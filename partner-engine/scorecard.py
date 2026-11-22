#!/usr/bin/env python3
"""Weekly partner scorecard.

Reads a referral export (Tolt-style CSV), applies the milestone tiers in
milestones.json, and writes:
  out/scorecard.md       - human-readable report (leaderboard, milestones hit, at-risk list)
  out/slack_payload.json - message ready for a Slack incoming webhook

If SLACK_WEBHOOK_URL is set, the message is also posted to Slack.
Standard library only, so it runs anywhere (laptop, GitHub Actions, cron).

Usage:
  python scorecard.py --export data/sample_tolt_export.csv --month 2026-11
"""
import argparse
import csv
import json
import os
import urllib.request
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).parent


def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tier_for(count, tiers):
    hit = None
    for t in sorted(tiers, key=lambda t: t["min"]):
        if count >= t["min"]:
            hit = t
    return hit


def prev_month(month):
    y, m = map(int, month.split("-"))
    return f"{y - 1}-12" if m == 1 else f"{y}-{m - 1:02d}"


def build(rows, cfg, month, today):
    cur, prev, rev, meta = defaultdict(int), defaultdict(int), defaultdict(int), {}
    for r in rows:
        pid = r["partner_id"]
        meta[pid] = r
        n = int(r["paid_referrals"] or 0)
        if r["month"] == month:
            cur[pid] += n
            rev[pid] += int(r["revenue_usd"] or 0)
        elif r["month"] == prev_month(month):
            prev[pid] += n

    partners = []
    for pid, r in meta.items():
        n, p = cur.get(pid, 0), prev.get(pid, 0)
        t, pt = tier_for(n, cfg["tiers"]), tier_for(p, cfg["tiers"])
        days = (today - datetime.strptime(r["joined"], "%Y-%m-%d").date()).days
        partners.append({
            "id": pid, "name": r["partner_name"], "type": r["partner_type"],
            "referrals": n, "last_month": p, "revenue": rev.get(pid, 0),
            "tier": t["name"] if t else "-",
            "new_tier": bool(t) and (not pt or t["min"] > pt["min"]),
            "reward": t["reward"] if t else "",
            "days": days,
        })
    partners.sort(key=lambda x: (-x["referrals"], x["name"]))

    risk, target = cfg["at_risk"], cfg["target_per_month"]
    return {
        "month": month,
        "partners": partners,
        "total_referrals": sum(p["referrals"] for p in partners),
        "total_revenue": sum(p["revenue"] for p in partners),
        "at_target": [p for p in partners if p["referrals"] >= target],
        "milestones": [p for p in partners if p["new_tier"]],
        "at_risk": [p for p in partners
                    if p["days"] >= risk["days_since_join"] and p["referrals"] <= risk["max_referrals"]],
        "ramping": [p for p in partners if p["days"] < risk["days_since_join"] and p["referrals"] == 0],
        "target": target,
    }


def to_markdown(s):
    L = [f"# Partner scorecard - {s['month']}", "",
         f"**{s['total_referrals']} paid referrals** - **${s['total_revenue']:,}** first-payment revenue - "
         f"**{len(s['at_target'])}/{len(s['partners'])}** partners at the {s['target']}/month target", "",
         "## Leaderboard", "", "| Partner | Type | Referrals | vs last month | Tier |", "|---|---|---:|---:|---|"]
    for p in s["partners"]:
        d = p["referrals"] - p["last_month"]
        L.append(f"| {p['name']} | {p['type']} | {p['referrals']} | {'+' if d >= 0 else ''}{d} | {p['tier']} |")
    L += ["", "## New milestones (send rewards)", ""]
    L += [f"- **{p['name']}** reached **{p['tier']}** -> {p['reward']}" for p in s["milestones"]] or ["- None this period"]
    L += ["", "## At risk (joined 3+ weeks ago, no paid referrals)", ""]
    L += [f"- {p['name']} ({p['type']}, {p['days']} days) -> run the activation play" for p in s["at_risk"]] or ["- None"]
    L += ["", "## Still ramping (under 3 weeks)", ""]
    L += [f"- {p['name']} ({p['days']} days)" for p in s["ramping"]] or ["- None"]
    return "\n".join(L) + "\n"


def to_slack(s):
    top = ", ".join(f"{p['name']} ({p['referrals']})" for p in s["partners"][:3])
    wins = "\n".join(f":trophy: *{p['name']}* hit *{p['tier']}*" for p in s["milestones"]) or "No new milestones."
    risk = "\n".join(f"- {p['name']}" for p in s["at_risk"]) or "None"
    return {"text": f"Partner scorecard {s['month']}", "blocks": [
        {"type": "header", "text": {"type": "plain_text", "text": f"Partner scorecard - {s['month']}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text":
            f"*{s['total_referrals']}* paid referrals - *${s['total_revenue']:,}* - "
            f"*{len(s['at_target'])}* partners at {s['target']}/mo\nTop 3: {top}"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": wins}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Needs a nudge:*\n{risk}"}},
    ]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", default=str(HERE / "data/sample_tolt_export.csv"))
    ap.add_argument("--month", default=date.today().strftime("%Y-%m"))
    ap.add_argument("--today", default=None, help="YYYY-MM-DD, for reproducible runs")
    args = ap.parse_args()

    cfg = json.loads((HERE / "milestones.json").read_text())
    today = datetime.strptime(args.today, "%Y-%m-%d").date() if args.today else date.today()
    s = build(load_rows(args.export), cfg, args.month, today)

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    md, payload = to_markdown(s), to_slack(s)
    (out / "scorecard.md").write_text(md, encoding="utf-8")
    (out / "slack_payload.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(md)

    hook = os.environ.get("SLACK_WEBHOOK_URL")
    if hook:
        req = urllib.request.Request(hook, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=15)
        print("Posted to Slack.")


if __name__ == "__main__":
    main()
