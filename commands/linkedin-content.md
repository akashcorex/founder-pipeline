# linkedin-content

Generates ready-to-publish posts for Akash Laha — a full-stack developer documenting his journey from developer to technical founder. Content spans system design, backend architecture, AI agents, SaaS, startup execution, and building in public.

**Voice foundation:** `./skills/content-engine/SKILL.md` for voice, `./skills/crosspost/SKILL.md` for platform adaptation (X vs LinkedIn).

---

## STEP 0 — Load the content doctrine

```bash
cat ./content-doctrine.md
```

Every post must pass the 4-part topic filter (Reach, Stakes, Altitude, Edge) and avoid the DROP list. We write about the technical founder journey — not coding tutorials, not tool config, not generic SaaS advice.

---

## STEP 1 — Fetch source material

```bash
curl -s -X POST \
  "https://api.apify.com/v2/acts/trudax~reddit-scraper-lite/run-sync-get-dataset-items?token=YOUR_APIFY_API_KEY&timeout=120&memory=1024" \
  -H "Content-Type: application/json" \
  -d '{
    "startUrls": [
      {"url": "https://www.reddit.com/r/ExperiencedDevs/top/?t=week"},
      {"url": "https://www.reddit.com/r/SaaS/top/?t=week"},
      {"url": "https://www.reddit.com/r/startups/top/?t=week"},
      {"url": "https://www.reddit.com/r/programming/top/?t=week"},
      {"url": "https://www.reddit.com/r/MachineLearning/top/?t=week"},
      {"url": "https://www.reddit.com/r/artificial/top/?t=week"}
    ],
    "maxItems": 60
  }'
```

Subreddits aligned with technical founder journey: r/ExperiencedDevs, r/SaaS, r/startups, r/programming, r/MachineLearning, r/artificial.

Fallback: Reddit JSON endpoints for these subreddits.

---

## STEP 2 — Research data for infographic

Use WebSearch to find a concrete dataset in the technical founder / SaaS / engineering niche. Target 6-10 data points with specific numbers. Good targets:
- Languages or frameworks by adoption / salary / satisfaction
- Startup failure reasons ranked by frequency
- AI / automation impact on developer productivity (real data)
- SaaS metrics benchmarks by stage (churn, CAC, LTV)
- Time allocation for developers vs founders (% coding vs meetings)
- Most valued engineering skills by hiring managers

---

## STEP 3 — Select source material for each post type

From gathered content, pick 4 completely distinct subjects. Every post must pass the 4-part topic filter.

- **BUILDING IN PUBLIC POST**: Something I shipped, broke, or learned. Real artifact, real outcome. First person, specific.
- **SYSTEMS / ARCHITECTURE POST**: A design decision, tradeoff, or pattern I wrestled with. Includes reasoning and outcome.
- **CAROUSEL**: A concept worth teaching visually — an architecture pattern, a mental model, a step-by-step framework. 7 slides, visual-first.
- **INFOGRAPHIC**: One striking dataset from Step 2. Data-driven, visual.

---

## STEP 4 — Write all posts

Apply every rule below without exception.

---

## WRITING RULES

### Voice

**First person.** I built this. I learned this. I was wrong about this. Every post is a chapter in the long-term story of becoming a technical founder.

**Tone:** Sharp, honest, builder-to-builder. Like DMing another dev who's also trying to ship. Not polished. Not corporate. Not LinkedIn-influencer.

**Authority earned through specificity.** Don't say "system design is important." Say "I spent 3 days refactoring our event bus because the fan-out pattern was creating race conditions on order processing."

### Voice examples

- "I spent two weeks building an AI agent that was supposed to automate our onboarding. It broke on day one in production. Here's what I missed."
- "Most devs I know want to start a SaaS. The thing that stops them isn't skill. It's not knowing which problem is worth solving."
- "I used to think microservices were always the answer. Then I built a monolith that scaled to 50k users on a $40 VPS."

### Post structure

1. **Hook** — Sharp, specific, makes the reader pause. I was wrong / I built / I discovered / I shipped.
2. **Context** — What I was doing, why it mattered. Brief. Grounded.
3. **The learning** — What went wrong, what worked, the insight. Concrete. Include real details.
4. **The takeaway** — What I'll do differently. What you can steal from this.
5. **Close** — Forward-looking. The next problem. What I'm building now. No generic "follow for more."

### Banned vocabulary

game-changer, revolutionary, cutting-edge, mind-blowing, insane, crazy (as hype), supercharge, unlock, level up, 10x, rocket ship, crushing it, killing it, dominated, so good, changed everything, blew my mind, you won't believe, this is the secret, the one thing, everyone is sleeping on, slept on, the best part?, here's the kicker, and it gets better, but wait, there's more

### Banned patterns

- "In today's rapidly evolving [anything]"
- "As a developer, I..."
- "I'm excited to share..."
- "Here's what I learned" (just say what you learned)
- "What do you think?" / "Agree?"
- "Thoughts?"
- "Drop a comment"
- Ending every post with a question
- LinkedIn-style praise stacking
- Fake vulnerability ("I was scared to post this")
- Journey / destination metaphors
- "Not [X]. [Y]." template hooks

### Formatting

- No em-dashes anywhere
- Sentence case for everything
- Varied sentence length — mix short with long
- Specific numbers > adjectives
- One idea per paragraph
- Skip periods on the last line sometimes — natural, not lazy

---

## STEP 5 — Carousel hook rotation

Read `./carousel-hook-log.json` before picking a style. Last style is banned. 3+ uses in last 7 is banned.

Pick from:

- **I Was Wrong** — "I was wrong about microservices" — share a corrected belief
- **Number Reveal** — "I tracked my coding hours for 30 days" — data from personal experience
- **System Breakdown** — "How I design backend systems (7 principles)" — framework / mental model
- **Mistake Story** — "The bug that cost me 3 days of debugging" — a specific failure
- **Before / After** — "My code before and after learning system design" — transformation
- **Unpopular Opinion** — "Most SaaS startups don't need Kubernetes" — contrarian, earned
- **Build Log** — "I built an AI agent. Here's the architecture." — shipped artifact
- **Trade-off** — "Monolith vs microservices: what I actually chose" — real decision

---

## OUTPUT FORMAT

Output each post separated by `━━━`. Nothing before the first separator.

━�━ BUILDING IN PUBLIC ━━━

[First person. What I built, shipped, broke, or learned. Real details — code, decisions, outcomes. 800-1500 chars. No CTA stacking.]

━━━ SYSTEMS POST ━━━

[Architecture decision, design pattern, or tradeoff I faced. Include the problem, the options I considered, what I chose, and the outcome. 800-1500 chars.]

━━━ CAROUSEL ━━━

Hook style: [from rotation]

Slide 1:
[Hook following the chosen style. 6-8 words max. Bold, clean. Curiosity gap.]

Slide 2:
[The problem or the setup. 1-2 sentences. Specific.]

Slide 3:
[Concept / principle 1. 1-2 sentences. Specific number or detail.]

Slide 4:
[Concept / principle 2. 1-2 sentences. Specific number or detail.]

Slide 5:
[Concept / principle 3. 1-2 sentences. Specific number or detail.]

Slide 6:
[The insight that ties it together. 1-2 sentences.]

Slide 7:
[CTA. "Follow @akashlaha for more on [specific topic]." Nothing else.]

Caption:
[Hook + one sentence summary + engagement question + single CTA. 4 lines max.]

━━━ INFOGRAPHIC ━━━

Generate a self-contained HTML file saved to `./linkedin-infographic.html`. The design must follow Gen Z aesthetic:
- Dark background (#0a0a0a or #0d0d0d)
- Bold sans-serif typography (Inter, system font stack)
- Accent color: #7C3AED (vibrant purple) or #06D6A0 (neon mint) — pick one per graphic
- Clean, minimal — no clutter, no grid lines, no chart junk
- 1080×1080px format
- Large bold numbers, minimal labels
- No external dependencies
- Data bars or donut chart or big-number hero — clean, modern, editorial
- Small attribution at bottom in subtle grey

---

## CROSSPOST RULES (apply when adapting for X)

From `./skills/crosspost/SKILL.md`:
- **X**: Lead with the sharpest claim. Compressed. Thread only if the argument needs it. No hashtags.
- **LinkedIn**: Add only context needed for people outside the niche. No fake reflection. No closing question just because.
- Never post identical copy across platforms.
- Each version reads like the same person under different constraints.
