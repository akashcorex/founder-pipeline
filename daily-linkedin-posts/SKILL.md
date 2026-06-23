---
name: daily-linkedin-posts
description: Multi-platform content pipeline for Akash Laha — a builder documenting his journey from developer to technical founder. Generates posts on system design, AI agents, SaaS, startup execution, and building in public. Crossposts to X and LinkedIn via Buffer.
---

# Daily Content Pipeline — Akash Laha

Generate today's content: building-in-public posts, systems/architecture writeups, AI agent experiments, and startup lessons. Carousel + infographic for visual posts. Crosspost to X and LinkedIn via Buffer.

---

## STEP 0 — Load the brand foundation

```bash
cat ./content-doctrine.md
```

`content-doctrine.md` defines the brand: Akash is a builder documenting his transformation from developer to technical founder. Every topic must pass the **4-part topic filter** (Reach, Stakes, Altitude, Edge) and avoid the **DROP list** (tutorials, tool config, AI workflow prompts, SaaS metrics without insight, dry news relay).

### 0B. Load the content engine (voice layer)

```bash
cat ./skills/content-engine/SKILL.md
```

The `content-engine` skill defines the canonical voice: first person, sharp, honest, builder-to-builder. Every post must follow its non-negotiables: real experience, one claim per post, specificity over adjectives, no engagement bait.

---

## STEP 1 — Fetch source material from Reddit

```bash
python3 fetch_reddit_apify.py
```

Subreddits: r/ExperiencedDevs, r/SaaS, r/startups, r/programming, r/MachineLearning, r/artificial.

If Apify fails:
```bash
python3 fetch_reddit_fallback.py
# or
python3 fetch_reddit_rss.py
```

Also fetch AI news:
```bash
python3 fetch_ai_news_rss.py
```

---

## STEP 2 — Research infographic data + select format

### 2A. Load infographic run-log (deduplication)

```bash
cat ./infographic-run-log.json 2>/dev/null || echo "[]"
```

Extract USED_INFOGRAPHIC_TOPICS (last 14 entries) and USED_FORMATS_RECENT (last 5). Last format is banned. 3+ uses in last 5 is banned.

### 2B. Find the dataset

WebSearch for a concrete dataset (2025-2026) with 6-10 data points in the technical founder lane:
- Languages / frameworks by usage, salary, satisfaction
- Startup failure reasons ranked
- AI impact on developer productivity
- SaaS metrics benchmarks
- Engineering skills valued by hiring managers
- Developer-to-founder time allocation stats

Topic must not overlap with USED_INFOGRAPHIC_TOPICS.

### 2C. Pick the infographic format

Read `./skills/illustration-formats/SKILL.md`. Apply its decision tree and format ban check. Record as INFOGRAPHIC_FORMAT and INFOGRAPHIC_TOPIC.

---

## STEP 3 — Select topics + write posts

### Step 3A — Topic selection

Pick 4 completely distinct subjects. Each must pass content-doctrine topic filter and sit in the technical founder lane.

```
TOPIC SELECTION:
1. BUILDING IN PUBLIC → [what I built / shipped / broke] — subject: [one phrase]
2. SYSTEMS / ARCHITECTURE → [design decision / tradeoff] — subject: [one phrase]
3. CAROUSEL → [concept / framework to teach visually] — subject: [one phrase]
4. INFOGRAPHIC → [INFOGRAPHIC_TOPIC from Step 2] — format: [INFOGRAPHIC_FORMAT]
```

Zero overlap check: all 4 subjects genuinely different.

### Step 3B — Write posts

Apply every rule from `./commands/linkedin-content.md`:

- First person voice. "I built this." "I was wrong about this."
- All content-engine hard bans enforced
- Real details — code, decisions, numbers, outcomes
- Post types: Building in Public, Systems/Architecture, Carousel (7 slides + caption), Infographic (data chart + caption)

Save to `./linkedin_posts_$(date +%Y%m%d).txt`

Generate infographic HTML → `./linkedin-infographic.html`

---

## STEP 4 — Run branded carousel (Gen Z aesthetic)

### 4A. Pick the carousel format

Read `./skills/branded-carousel/FORMATS.md`. Available formats updated for Gen Z taste:
- `DARK_MINIMAL` — bold typography, clean structure, dark background
- `SYSTEM_BREAKDOWN` — architecture diagrams, numbered principles
- `BUILD_LOG` — shipped artifact, before/after, code → result
- `DATA_STORY` — stats-driven, clean charts, numbers-first
- `CONTRARIAN_TAKE` — unpopular opinion, bold claim, earned perspective
- `FRAMEWORK` — step-by-step model, visual progression

### 4B. Pick the carousel hook style

```bash
cat ./carousel-hook-log.json 2>/dev/null || echo "[]"
```

Last style is banned. 3+ uses in last 7 is banned. Pick from the updated hook rotation in `./commands/linkedin-content.md` (Step 5).

### 4C. Source images

Minimum 4 images from Unsplash (`https://source.unsplash.com/1080x1080/?[keyword]`) with dark/tech/abstract themes. No stock-photo corporate aesthetic.

### 4D. Run branded-carousel skill

Run `./skills/branded-carousel/SKILL.md` with the Gen Z dark aesthetic:
- Dark backgrounds (#0a0a0a, #0d0d0d, #111)
- Bold modern typography (Inter, Satoshi)
- Accent colors: #7C3AED (purple), #06D6A0 (mint), or #FF6B6B (coral)
- Clean, minimal — no clutter, no drop shadows, no gradients

PDF output: `./carousel-routine/output/$(date +%Y-%m-%d)/carousel-branded/*.pdf`

### 4E. Write carousel hook entry to run-log

```bash
python3 - << 'PYEOF'
import json, os, datetime
LOG_PATH = "./carousel-hook-log.json"
try:
    with open(LOG_PATH) as f: log = json.load(f)
except (FileNotFoundError, json.JSONDecodeError): log = []
entry = {
    "date": datetime.date.today().isoformat(),
    "hook_style": "CAROUSEL_HOOK_STYLE_PLACEHOLDER",
    "hook_text": "CAROUSEL_HOOK_TEXT_PLACEHOLDER",
    "carousel_topic": "CAROUSEL_TOPIC_PLACEHOLDER",
    "carousel_format": "CAROUSEL_FORMAT_PLACEHOLDER"
}
log.append(entry)
log = log[-30:]
with open(LOG_PATH, "w") as f: json.dump(log, f, indent=2)
print(f"Carousel hook log updated: {entry['hook_style']} — {entry['hook_text']}")
PYEOF
```

Replace all PLACEHOLDER values before running.

---

## STEP 5 — Screenshot infographic (1080×1080 PNG)

```bash
python3 capture_html.py --input ./linkedin-infographic.html --output ./linkedin-infographic-$(date +%Y%m%d).png --width 1080 --height 1080
```

### 5B. Write infographic entry to run-log

```bash
python3 - << 'PYEOF'
import json, os, datetime
LOG_PATH = "./infographic-run-log.json"
try:
    with open(LOG_PATH) as f: log = json.load(f)
except (FileNotFoundError, json.JSONDecodeError): log = []
entry = {"date": datetime.date.today().isoformat(), "topic": "INFOGRAPHIC_TOPIC_PLACEHOLDER", "format": "INFOGRAPHIC_FORMAT_PLACEHOLDER", "generated_at": datetime.datetime.utcnow().isoformat() + "Z"}
log.append(entry)
log = log[-30:]
with open(LOG_PATH, "w") as f: json.dump(log, f, indent=2)
print(f"Infographic run-log updated: {entry['topic']} ({entry['format']})")
PYEOF
```

Replace PLACEHOLDER values before running.

---

## STEP 6 — Generate AI / tech news posts (linkedin-ai-news-engine)

```bash
cat ./skills/linkedin-ai-news-engine/SKILL.md
```

Execute the full skill. Apply content-engine voice rules (first person, builder perspective). Reframe all content through the technical founder lens — what does this news mean for builders? Save to `./ai_news_posts_$(date +%Y%m%d).txt`.

---

## STEP 7 — Generate performance posts (linkedin-performance-engine)

```bash
cat ./skills/linkedin-performance-engine/SKILL.md
```

Execute the full skill. Reads `./founderswing_linkedin_content_report.md` if available. Apply content-engine voice. Save to `./performance_posts_$(date +%Y%m%d).txt`.

---

## STEP 8 — Crosspost: adapt for X vs LinkedIn

```bash
cat ./skills/crosspost/SKILL.md
```

For each post, produce:
1. LinkedIn version (primary — full context, first person, builder voice)
2. X version (compressed — lead with sharpest claim, no hashtags, thread only if needed)

Never post identical copy. Each version = same person, different constraints.

---

## STEP 9 — Build schedule and send to Buffer

### 9A. Build schedule.json

```bash
python3 build_schedule.py \
  --posts-file ./linkedin_posts_today.txt \
  --ai-news-file ./ai_news_posts_$(date +%Y%m%d).txt \
  --perf-file ./performance_posts_$(date +%Y%m%d).txt
```

Edit `schedule.json` with publicly hosted media URLs for carousel / infographic.

### 9B. Dry run + schedule

```bash
python3 schedule_via_buffer.py --schedule-file schedule.json --dry-run
python3 schedule_via_buffer.py --schedule-file schedule.json
```

Posts go to both LinkedIn and X via Buffer. IST times auto-converted to UTC.

### 9C. Completion report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Daily Content — {DATE}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Building in Public: ✓
Systems / Architecture: ✓
Carousel: ✓ (Gen Z dark aesthetic)
Infographic: ✓ (dark mode)
Crosspost (X + LinkedIn): ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Buffer Scheduling: ✓
  LinkedIn: N posts | X: N posts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
