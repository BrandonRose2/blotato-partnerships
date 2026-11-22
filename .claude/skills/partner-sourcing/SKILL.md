---
name: partner-sourcing
description: Find, score and draft outreach for new Blotato partners (creators and agencies). Use when asked to source partners, build a lead list or run weekly prospecting.
---

# Partner sourcing

1. Pick 3 to 5 search angles for this week (for example "n8n social media automation", "faceless YouTube workflow", "social media agency for coaches").
2. Collect candidates:
   - YouTube: `python partner-engine/source_partners.py --youtube "<query>" ...` (needs `YOUTUBE_API_KEY`)
   - Other sources (TikTok, X lists, agency directories, newsletters): scrape into a CSV with the columns in `partner-engine/data/sample_candidates.csv`, then run `--csv <file>`.
3. Review `partner-engine/out/partner_leads.csv`. Keep scores of 50 and up. Spot-check the top 10 by hand, because a score is a filter, not a decision.
4. For each kept lead, open their latest post and rewrite the drafted `opener` so it references something real and specific.
5. Skip anyone already in the partner list, and anyone who has said no in the last 90 days.
6. Report: how many sourced, how many kept, the top 5 with one line on why each one fits.
