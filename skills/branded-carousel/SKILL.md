---
name: branded-carousel
description: Creates a Gen Z dark aesthetic carousel (7 slides, 1080×1080 PNG + PDF) from a given topic. Dark mode, bold typography, clean minimal layout. No corporate templates.
argument-hint: "[topic + carsousel format]"
allowed-tools: WebFetch, WebSearch, Bash, Read, Write
---

You are the carousel engine for Akash Laha's content. You produce one polished, Gen Z dark aesthetic carousel per run — 7 slides, dark backgrounds, bold modern typography.

Follow every phase in strict order.

---

## PHASE 0 — Bootstrap

### 0A: Paths
```
CAROUSEL_DIR = ./carousel-routine
TEMP_DIR     = $CAROUSEL_DIR/temp/carousel-branded
ASSETS_DIR   = $TEMP_DIR/assets
DATE         = $(date +%Y-%m-%d)
OUTPUT_DIR   = $CAROUSEL_DIR/output/$DATE/carousel-branded
```

### 0B: Parse Input
Extract: TOPIC, FORMAT (from FORMATS.md), HOOK_STYLE (from rotation).

### 0C: Create Directories
```bash
mkdir -p "$OUTPUT_DIR" "$ASSETS_DIR"
rm -f "$TEMP_DIR/slide-"*.html 2>/dev/null
```

---

## PHASE 1 — Image Sourcing

### 1A: Source Real Images

Minimum 4 images. Dark, moody, high contrast aesthetic. Sources:
- `https://source.unsplash.com/1080x1080/?[keyword]` — use keywords like "technology-dark", "code-dark", "server-room", "minimal-dark", "architecture-dark"
- Product screenshots if available
- Diagrams or architecture sketches if relevant

### 1B: Verify Images
Each image must be >10KB. Remove any that fail.

---

## PHASE 2 — Design System

### Color Palette
```
Dark bg:         #0a0a0a
Card surface:    #111111
Raised surface:  #1a1a1a
Border subtle:   #2a2a2a
Text primary:    #FFFFFF
Text secondary:  #A1A1A1
Text muted:      #666666

Accent (pick one per carousel):
  Purple: #7C3AED  (systems, AI, architecture)
  Mint:   #06D6A0  (growth, SaaS, metrics)
  Coral:  #FF6B6B  (opinions, stories)
  Amber:  #F59E0B  (data, numbers)
```

### Typography
```
font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;

Headlines:  Inter 700-800, tracking: -0.5px, sentence case
Body:       Inter 400-500, 18-22px, line-height: 1.5
Numbers:    Inter 800, 48-72px (hero stats)
Accents:    Instrument Serif italic (optional, one word per slide max)
```

### Layout Constants
```
Width:  1080px
Height: 1080px
Padding: 60px all sides (slide number outside padding)
Slide number: top-right, 14px, color #444, Inter 400
```

---

## PHASE 3 — Slide HTML Generation

Write 7 HTML files to `$TEMP_DIR/slide-01.html` through `slide-07.html`.

### Shared HTML Template
```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap');
  
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1080px; height: 1080px;
    background: #0a0a0a;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #FFFFFF;
    overflow: hidden;
    position: relative;
  }
  .slide-number {
    position: absolute; top: 40px; right: 60px;
    font-size: 14px; color: #444;
    font-weight: 400;
  }
  .container {
    padding: 80px 60px 60px 60px;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  h1 { font-size: 52px; font-weight: 800; line-height: 1.1; letter-spacing: -0.5px; }
  h2 { font-size: 36px; font-weight: 700; line-height: 1.2; }
  p { font-size: 22px; font-weight: 400; line-height: 1.5; color: #A1A1A1; }
  .hero-number { font-size: 72px; font-weight: 800; }
  .accent { color: ACCENT_COLOR; }
  .italic { font-family: 'Instrument Serif', serif; font-style: italic; }
  .full-bleed-bg {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    object-fit: cover; z-index: -1;
  }
  .overlay {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.6); z-index: 0;
  }
  .content { position: relative; z-index: 1; }
</style>
</head>
<body>
  <div class="slide-number">01 / 07</div>
  <!-- slide content -->
</body>
</html>
```

### Slide Content Rules

**Slide 1 (Hook):** Bold statement, 6-8 words max. Centered or bottom-aligned. No image (or subtle dark abstract). Creates curiosity gap.

**Slide 2 (Context):** One image (full-bleed with overlay) + 1-2 sentences. What's the problem or setup.

**Slides 3-5 (Body):** Core content. Each slide = one point, one visual element (image, number, or icon). Dark card surfaces for text-heavy slides.

**Slide 6 (Insight):** The synthesis. Bold text, minimal. Ties the carousel together.

**Slide 7 (CTA):** Single line. "Follow @akashlaha for more on [topic]." Or "Save this. Building more."

Replace ACCENT_COLOR with the chosen hex value for each slide.

---

## PHASE 4 — Rendering

### 4A: Render PNGs
```bash
cd "$CAROUSEL_DIR" && node render.js "$DATE" "carousel-branded"
```

### 4B: Compile PDF
```bash
cd "$CAROUSEL_DIR" && node render-pdf.js "$DATE" "carousel-branded"
```

⚠️ Always build PDF from PNGs via `render-pdf.js`, never from `page.pdf()`.

### 4C: Verify Output
```bash
ls -la "$OUTPUT_DIR/"*.png "$OUTPUT_DIR/"*.pdf
```
Each PNG must exist and be >20KB. PDF must exist and be >50KB.

---

## PHASE 5 — Update Run Log

```bash
python3 - << 'PYEOF'
import json, os, datetime
LOG_PATH = "./carousel-hook-log.json"
try:
    with open(LOG_PATH) as f: log = json.load(f)
except (FileNotFoundError, json.JSONDecodeError): log = []
entry = {
    "date": datetime.date.today().isoformat(),
    "hook_style": "HOOK_STYLE",
    "hook_text": "HOOK_TEXT",
    "carousel_topic": "TOPIC",
    "carousel_format": "FORMAT"
}
log.append(entry)
log = log[-30:]
with open(LOG_PATH, "w") as f: json.dump(log, f, indent=2)
PYEOF
```

Replace HOOK_STYLE, HOOK_TEXT, TOPIC, FORMAT with actual values.

---

## Quality Gate

- All 7 slides render without visual bugs
- Dark background (#0a0a0a) consistent across all slides
- Accent color consistent across all slides
- No em-dashes anywhere
- Slide numbers correct (01/07 through 07/07)
- PDF built from PNGs (not HTML re-render)
- At least 4 slides have real images
- No "Founders Wing" or "Prithal" anywhere — this is Akash Laha's brand
