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
GEMINI_API_KEY=...          # Required: post + visual-layout generation (generate_posts_via_gemini.py)
BUFFER_API_KEY=...          # Required: Buffer API key for scheduling posts
APIFY_API_KEY=...           # Optional: primary Reddit fetch method (fetch_reddit_apify.py). Falls back to JSON/RSS scraping if absent.
OPENROUTER_API_KEY=...      # Optional: banned-word correction pass (correct_posts.py). Pipeline still runs without it.
SCRAPINGDOG_API_KEY=...     # Optional: for X/Twitter research (used by the linkedin-ai-news-engine skill, not by any .py script)
BUFFER_LINKEDIN_CHANNEL_ID= # Optional: LinkedIn channel ID override (auto-detected otherwise)
BUFFER_X_CHANNEL_ID=        # Optional: X/Twitter channel ID override (auto-detected otherwise)
```

> Channel IDs are auto-detected from your Buffer account. Set the two `BUFFER_*_CHANNEL_ID` vars only if you need to override auto-detection (e.g. multiple LinkedIn channels on the account) — `schedule_via_buffer.py` reads them first and only falls back to auto-detection if they're unset.

> `.env` is loaded once via `env_utils.py`, which resolves the file relative to the project root (not your current shell directory) and lets real exported environment variables override `.env` values. All scripts share this loader — there's no more per-file, hand-rolled `.env` parsing, and no more disabled SSL certificate verification (a previous version of every network script disabled TLS verification entirely; `env_utils.new_ssl_context()` now uses a normal, verifying SSL context everywhere).

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
│  └── LinkedIn by default (X opt-in), 3 days, IST     │
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
| `generate_posts_via_gemini.py` | LLM post + visual-layout generation via Google Gemini (name reflects what it actually calls) |
| `correct_posts.py` | Post-processing: fix banned words via OpenRouter |

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
| `run_pipeline.py` | **One-command orchestrator** — fetch → generate → correct → build schedule → dry-run/schedule via Buffer |
| `buffer_client.py` | Buffer GraphQL API client |
| `schedule_via_buffer.py` | Schedule posts to LinkedIn (+ X, opt-in) |
| `build_schedule.py` | Build schedule.json from pipeline output |
| `schedule.json.example` | Example schedule format |
| `buffer.md` | Buffer API reference docs |
| `env_utils.py` | Shared `.env` loader + verifying SSL context, used by every script that calls a network API |

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

### Quick Start — one command

For the scriptable part of the pipeline (fetch → generate → correct → build schedule → preview/schedule via Buffer), use `run_pipeline.py` instead of running each phase by hand:

```bash
# Safe by default: fetches, generates, and shows exactly what WOULD be scheduled.
# Nothing is posted to Buffer until you pass --live.
python3 run_pipeline.py

# Actually schedule the previewed posts to Buffer (LinkedIn only, by default)
python3 run_pipeline.py --live

# Reuse already-fetched data instead of re-scraping Reddit/AI news
python3 run_pipeline.py --skip-fetch --live

# Attach hosted carousel/infographic images (see Phase 3 below for how to render them)
python3 run_pipeline.py --carousel-url https://... --infographic-url https://... --live
```

This covers Phases 1, 2 (LLM path), and 5. It does **not** render carousel/infographic
visuals (Phase 3) or hand-craft distinct X copy (Phase 4) — those remain
creative/agent-assisted steps, described below. Without a hosted image URL, the
carousel/infographic posts are simply scheduled as text-only.

The rest of this section documents each phase individually, for the manual /
agent-driven (SKILL.md) workflow, or if you want to run a single phase on its own.

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
python3 generate_posts_via_gemini.py
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
# Build schedule.json from generated posts (LinkedIn only, by default)
python3 build_schedule.py

# Opt into crossposting to X too — only do this if you've actually written
# separate, X-length copy per the crosspost skill. Otherwise the same
# LinkedIn-length caption gets sent to X as-is and will likely be rejected.
python3 build_schedule.py --target both

# Preview (dry run)
python3 schedule_via_buffer.py --schedule-file schedule.json --dry-run

# Schedule all posts
python3 schedule_via_buffer.py --schedule-file schedule.json
```

Posts are scheduled via Buffer's GraphQL API with `customScheduled` mode at the specified IST times (auto-converted to UTC). **LinkedIn is the default and only target** — this is a LinkedIn-first pipeline, posts are written at LinkedIn length (800–1500 chars), and there's no automated per-platform copy adaptation, so blasting the same text to X by default was more likely to break posts than help. Pass `--target both` to `build_schedule.py` once you've wired in real X-adapted copy. `schedule_via_buffer.py` also now warns if a caption exceeds LinkedIn's (~3000 char) or X's (~280 char) limits before sending. Media images require publicly hosted URLs — upload to Cloudinary, Cloudflare R2, or similar before scheduling.

**To list available channels:**
```bash
python3 schedule_via_buffer.py --list-channels
```

---

## Post Schedule (4 posts/day × 3 days → LinkedIn by default, X opt-in)

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

`skills/linkedin-performance-engine/SKILL.md` (Step 7) reads an optional `founderswing_linkedin_content_report.md` file for performance-post input. **This report is not included in the repo** — it's an external analytics export you supply yourself; without it, Step 7 has nothing to reason about and performance posts should be skipped. That report (when supplied) was explicit that the account's current ~25-35 posts/week is **suppressing reach** and recommends **≤7 posts/week**. This pipeline produces 16 posts/day, which runs against that finding. The performance posts were added per an explicit "add on top" decision; the volume-reduction recommendation is intentionally **deferred, not resolved.** Revisit whether to cut overall cadence before scaling output further.

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
