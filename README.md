# Multi-Platform Content Pipeline — Akash Laha

> Generates content from Reddit + tech news + personal experience. Uses `content-engine` for voice, `crosspost` for LinkedIn/X adaptation, and Buffer for scheduling. Gen Z dark aesthetic for all visual assets.

> **Personal brand:** Akash is a full-stack developer documenting his journey from developer to technical founder. Every post is first person, sharp, and grounded in real experience — what he's building, learning, and shipping. The pipeline is governed by [`content-doctrine.md`](content-doctrine.md).

---

## Prerequisites

### Software
- **Node.js** ≥ 18 (for carousel rendering via Puppeteer)
- **Python 3.10+** (for data fetching, LLM generation, and scheduling)

### API Keys (stored in `.env`)
```
OPENROUTER_API_KEY=...      # For LLM post generation
ANTHROPIC_API_KEY=...       # Alternative LLM provider
SCRAPINGDOG_API_KEY=...     # Optional: for X/Twitter research
BUFFER_API_KEY=...          # Buffer API key for scheduling posts
BUFFER_LINKEDIN_CHANNEL_ID= # Optional: LinkedIn channel ID override
BUFFER_X_CHANNEL_ID=        # Optional: X/Twitter channel ID override
```

> Channel IDs are auto-detected from your Buffer account. Set these env vars only to override.

### NPM Dependencies
```bash
cd carousel-routine && npm install
```

---

## Pipeline Overview (16 posts = 4 Reddit + 7 AI News + 5 Performance)

```
┌─────────────────────────────────────────────────────┐
│  PHASE 1: DATA FETCHING                              │
│  ├── Reddit: 6 subreddits via Apify / JSON / RSS    │
│  └── AI News: RSS feeds, newsletters                 │
├─────────────────────────────────────────────────────┤
│  PHASE 2: CONTENT GENERATION (skills + LLM)          │
│  ├── content-engine: voice foundation + hard bans    │
│  ├── 4 Reddit posts: Article, Poll, Carousel, Info   │
│  ├── 7 AI News posts (linkedin-ai-news-engine)       │
│  └── 5 Performance posts (linkedin-performance)      │
├─────────────────────────────────────────────────────┤
│  PHASE 3: VISUAL ASSETS                              │
│  ├── Carousel: 7 slides → PNG → PDF                 │
│  └── Infographic: HTML → PNG via capture_html.py     │
├─────────────────────────────────────────────────────┤
│  PHASE 4: CROSSPOST ADAPTATION                       │
│  ├── crosspost skill: adapt voice per platform       │
│  └── LinkedIn (context) + X (compressed) versions    │
├─────────────────────────────────────────────────────┤
│  PHASE 5: SCHEDULING (via Buffer API)                │
│  ├── build_schedule.py: assemble schedule.json       │
│  ├── schedule_via_buffer.py: push to Buffer          │
│  └── LinkedIn + X, 3 days, IST times                 │
└─────────────────────────────────────────────────────┘
```

---

## File Reference

### 🧠 Skills (the brain)

| File | Purpose |
|------|---------|
| `daily-linkedin-posts/SKILL.md` | **Master orchestrator** — the full 9-step pipeline |
| `skills/content-engine/SKILL.md` | **Voice foundation** — writing rules, hard bans, quality gate |
| `skills/crosspost/SKILL.md` | **Platform adaptation** — X vs LinkedIn voice differences |
| `skills/branded-carousel/SKILL.md` | Carousel design system, slide layouts |
| `skills/branded-carousel/FORMATS.md` | 6 carousel format templates |
| `skills/illustration-formats/SKILL.md` | 5 infographic format recipes |
| `skills/linkedin-ai-news-engine/SKILL.md` | AI news engine — 7 archetypes |
| `skills/linkedin-performance-engine/SKILL.md` | Performance engine — 5 report-driven posts |
| `commands/linkedin-content.md` | Post writing rules, archetypes, banned words |
| `content-doctrine.md` | North star: topic filter, DROP list, positioning |

### 📡 Data Fetching

| File | Purpose |
|------|---------|
| `fetch_reddit_apify.py` | Primary: Reddit via Apify API |
| `fetch_reddit_fallback.py` | Fallback: Reddit JSON endpoints |
| `fetch_reddit_rss.py` | Last resort: Reddit RSS feeds |
| `fetch_ai_news_rss.py` | AI news from RSS feeds |

### ✍️ Content Generation

| File | Purpose |
|------|---------|
| `generate_posts_via_openrouter.py` | LLM post generation via OpenRouter/Gemini |
| `write_today_data.py` | Master script: combine posts into output file |
| `correct_posts.py` | Post-processing: fix banned words, formatting |

### 🎨 Visual Assets

| File | Purpose |
|------|---------|
| `carousel-routine/render.js` | HTML slides → 1080×1080 PNGs |
| `carousel-routine/render-pdf.js` | PNGs → compiled PDF |
| `carousel-routine/compile_pdf.js` | Alternative PDF compiler |
| `carousel-routine/screenshot_all.js` | Batch screenshot all slides |
| `carousel-routine/brand-kit.html` | Brand design system HTML |
| `carousel-routine/capture_source.js` | Capture product images from source URLs |
| `capture_html.py` | Generic HTML → PNG capture via Puppeteer |
| `linkedin-infographic-template.html` | Base infographic HTML template |

### 📅 Scheduling (Buffer API)

| File | Purpose |
|------|---------|
| `buffer_client.py` | Buffer GraphQL API client |
| `schedule_via_buffer.py` | Schedule posts to LinkedIn + X |
| `build_schedule.py` | Build schedule.json from pipeline output |
| `schedule.json.example` | Example schedule format |
| `buffer.md` | Buffer API reference docs |

### 📋 State & Log Files
| File | Purpose |
|------|---------|
| `carousel-hook-log.json` | History of carousel hook styles (for rotation) |
| `infographic-run-log.json` | History of infographic topics (for deduplication) |
| `performance-run-log.json` | History of performance-engine subjects (contrarian belief, poll, etc.) so they don't repeat day to day |
| `scheduled_history.json` | History of scheduled posts |
| `reddit_data.json` | Latest fetched Reddit data |
| `ai_news_data.json` | Latest fetched AI news data |

---

## How to Run

### Phase 1: Fetch Data
```bash
# Try Apify first (most reliable, requires API key)
python3 fetch_reddit_apify.py

# If Apify fails, try JSON endpoints
python3 fetch_reddit_fallback.py

# If JSON blocked (403/429), fall back to RSS
python3 fetch_reddit_rss.py

# Fetch AI news RSS
python3 fetch_ai_news_rss.py
```

### Phase 2: Generate Content
The AI agent follows skill instructions:
- `skills/content-engine/SKILL.md` → voice foundation for all posts
- `commands/linkedin-content.md` → 4 Reddit-based posts
- `skills/linkedin-ai-news-engine/SKILL.md` → 7 AI news posts
- `skills/linkedin-performance-engine/SKILL.md` → 5 performance posts

Or use the LLM script:
```bash
python3 generate_posts_via_openrouter.py
```

### Phase 3: Build Visual Assets

**Carousel:**
```bash
# Agent generates slide HTML in carousel-routine/temp/
# Render slides to PNG
cd carousel-routine && node render.js
# Compile PNGs to PDF
node render-pdf.js
```

**Infographic:**
```bash
# Agent generates linkedin-infographic.html
# Screenshot to 1080×1080 PNG
python3 capture_html.py --input linkedin-infographic.html --output linkedin-infographic-$(date +%Y%m%d).png
```

### Phase 4: Crosspost Adaptation
AI agent runs `skills/crosspost/SKILL.md` to produce platform-specific versions:
- LinkedIn: context for broader audience
- X: compressed, sharpest claim first

### Phase 5: Schedule via Buffer
```bash
# Build schedule.json from generated posts
python3 build_schedule.py

# Preview (dry run)
python3 schedule_via_buffer.py --schedule-file schedule.json --dry-run

# Schedule all posts to LinkedIn + X
python3 schedule_via_buffer.py --schedule-file schedule.json
```

Posts are scheduled via Buffer's GraphQL API with `customScheduled` mode at the specified IST times (auto-converted to UTC). Both LinkedIn and X channels are targeted by default. Media images require publicly hosted URLs — upload to Cloudinary, Cloudflare R2, or similar before scheduling.

**To list available channels:**
```bash
python3 schedule_via_buffer.py --list-channels
```

---

## Post Schedule (4 posts/day × 3 days → LinkedIn + X)

| Day | Time (IST) | Post Type | Content Source |
|-----|-----------|-----------|---------------|
| Day 1 | 9:00 AM | Carousel (image) | Reddit |
| Day 1 | 12:00 PM | Infographic (image) | Reddit + Data |
| Day 1 | 3:00 PM | Collaborative Article (text) | Reddit |
| Day 1 | 6:00 PM | Poll → Text | Reddit |
| Day 2 | 9:00 AM | Tool Spotlight (text) | AI News |
| Day 2 | 12:00 PM | Weekly Roundup (text) | AI News |
| Day 2 | 3:00 PM | Plain English (text) | AI News |
| Day 2 | 6:00 PM | Unfair Advantage (text) | AI News |
| Day 3 | 9:00 AM | Career/Income (text) | AI News |
| Day 3 | 12:00 PM | Hot Take (text) | AI News |
| Day 3 | 3:00 PM | Steal This (text) | AI News |

> **Note:** The 5 report-driven performance posts (STEP 7) are **delivered for review/manual posting but are not yet wired into the LinkedIn auto-scheduler.** Scheduling them automatically is a separate task. See the cadence caveat below.

### ⚠️ Cadence caveat (from the analytics report)

The `founderswing_linkedin_content_report.md` is explicit that the account's current ~25-35 posts/week is **suppressing reach** and recommends **≤7 posts/week**. This pipeline produces 16 posts/day, which runs against that finding. The performance posts were added per an explicit "add on top" decision; the volume-reduction recommendation is intentionally **deferred, not resolved.** Revisit whether to cut overall cadence before scaling output further.

---

## Deduplication Rules

- **Carousel hooks**: Read `carousel-hook-log.json` before picking a style. Last used style is banned. Any style with 3+ uses in last 7 entries is also banned.
- **Infographic topics**: Read `infographic-run-log.json`. Never repeat a topic from the last 30 days.
- **Post topics**: No two posts in the same batch can cover the same Reddit thread or story.
- **Performance posts**: Read `performance-run-log.json` before writing. The contrarian belief and poll topic from the last 14 runs are banned. All 5 performance subjects must be distinct from each other and from the day's other 11 posts (16 unique subjects total).

---

## Sample Outputs

The `sample-outputs/` folder contains a complete set from the June 12, 2026 run:
- `linkedin_posts_20260612.txt` — All 11 posts in text format
- `linkedin_posts_20260612.html` — Carousel HTML slides
- `linkedin_posts_20260612.pdf` — Compiled carousel PDF
- `linkedin-infographic-20260612.png` — Infographic PNG
