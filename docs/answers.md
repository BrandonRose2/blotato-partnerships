# My answers

## 1. How would you recruit my next 1,000 partners?

**Strategy: turn Blotato's own happy customers into partners.**

The best partners already use the product every day. They have real results to show and an audience that trusts them, and many of them are creators and agencies who are already being asked "what do you use to post everywhere?"

How I'd run it:
- **Trigger the invite at the "aha" moment,** not at signup. For example, the day a customer passes their 30th scheduled post, or after two weeks of steady use, they get an in-app and email invite: *"You've shipped 30 posts with Blotato. Want to earn 50% when your audience does the same?"*
- **Hand them a ready-to-post kit:** a "how I automate my content" script, three hooks, and their own usage stats ("I posted 120 times last month without opening 11 apps"). That way their first post takes ten minutes, not a weekend.
- **Book a 15-minute call** with the top 10% by usage and audience size. Those are the future Elite partners.

Why this one: it's the warmest pool there is. These people already believe in the product, so I'm not convincing anyone, I'm just giving them a reason and a script. It's also measurable from day one: invites sent, accepted, first post, first referral.

## 2. How would you recruit my next 10,000 partners?

**Strategy: a template partner program, where automation builders publish workflows that run on Blotato.**

Blotato is agent infrastructure: one API and MCP server for 11 platforms. That means every n8n, Make, Claude Code or Codex workflow that ends with "...and post it everywhere" can run on Blotato. Thousands of builders already share these workflows on YouTube, in the n8n and Make communities, on GitHub and in Skool groups.

How I'd run it:
- **Recruit the builders.** I'd scrape the n8n and Make template galleries, GitHub and YouTube automation tutorials for people already publishing social-posting workflows. Then I'd score and rank them (see `partner-engine/source_partners.py`) and reach out with a specific, personal first line.
- **Give them a home:** a "Built with Blotato" template gallery where every template carries the builder's referral link and a badge, plus a monthly leaderboard.
- **Make templates the reward currency:** featured placement, co-marketing on Sabrina's channels for the best ones, and bonuses at milestones.

Why this one: it scales on assets, not effort. A creator's post fades in 48 hours. A good template keeps getting found, copied and referred for months without the partner doing anything more. It's also self-serve, so 10,000 partners doesn't need 10,000 calls. And it fits where Blotato is going: the more agents and automations people build, the more templates exist.

## 3. What system would you build to accomplish that in 3 months?

**The Partner Engine.** The skeleton is in this repo:

| Stage | What it does | Built with |
|---|---|---|
| Source | Scrape and score creators, agencies and template builders weekly | `source_partners.py`, YouTube Data API, scheduled job |
| Reach out | Personal first lines drafted, reviewed by a human, sent in batches | `partner-sourcing` Claude Code skill |
| Onboard | Welcome message, 30-day plan and content kit per partner | `partner-onboarding` skill, Blotato MCP |
| Activate | Day 7/14/30 check-ins; at-risk partners flagged automatically | `scorecard.py` at-risk rules |
| Reward | Milestone tiers (1 / 3 / 10 / 25 referrals a month) with rewards | `milestones.json` |
| Community | Unanswered Slack threads triaged and drafted; FAQ built weekly | `slack-community-answers` skill, Slack MCP |
| Measure | Weekly scorecard to Slack, history committed to the repo | GitHub Actions cron |

**Month 1, foundation:** connect the Tolt referral data, ship the weekly scorecard, launch the customer-to-partner invite (strategy 1), and set the baseline numbers.
**Month 2, activation:** onboarding plans for every new partner, at-risk nudges, milestone rewards live, and the Slack triage agent running with a human reviewing.
**Month 3, scale:** launch the template gallery and builder sourcing (strategy 2), run outreach in weekly batches, and double down on whatever the scorecard shows is working.

The one number I'd watch: **the share of partners at 10+ paid referrals a month**, not the total partner count.

## 4. Your most impressive accomplishment?

I was hired as an executive assistant at a property management company with no engineering team. Between February and November 2026 I taught myself to build with AI and shipped **more than 20 working tools** that the company actually used.

The one I'm proudest of is the **live vacancy dashboard and daily executive report**. It started with four regions and grew to **41 properties, 5 regions and 3,917 units**. Every day at 1 PM it emailed a polished HTML report to the CEO and top executives in New York: per-unit vacancy, leased/preleased status, day-over-day changes and cash flow.

The early versions broke. Live sync failed and the email formatting fell apart. I kept rebuilding until it ran every day without anyone touching it. That's the part I'm proudest of. Struggling, feeling dumb and failing until it works is the job you're describing, and it's how I've been working all year.
