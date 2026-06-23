---
name: illustration-formats
description: Five infographic formats with Gen Z dark aesthetic. Picks the right visual format for any dataset and renders a 1080x1080 PNG ready for LinkedIn and X.
---

# Illustration Format Library — Dark Aesthetic

Five infographic formats. Select based on data shape, render HTML, screenshot to 1080×1080 PNG.

## Format Selection

```
1. RANKED LIST with 6-10 items → RANKED_BARS
2. PARTS_OF_A_WHOLE breakdown → DONUT_BREAKDOWN
3. CHANGE_OVER_TIME / growth → TIMELINE_SHIFT
4. HEAD_TO_HEAD comparison → COMPARISON_SPLIT
5. SINGLE BIG STAT + context → HERO_NUMBER
Default → RANKED_BARS
```

## Shared Design System — Gen Z Dark

### Color Palette
```
Background:       #0a0a0a
Card surface:     #111111
Raised surface:   #1a1a1a
Border:           #2a2a2a
Text primary:     #FFFFFF
Text secondary:   #A1A1A1
Text muted:       #666666

Accent (pick one per infographic):
  Purple: #7C3AED  (tech, systems, AI)
  Mint:   #06D6A0  (growth, metrics, SaaS)
  Coral:  #FF6B6B  (opinions, contrasts)
  Amber:  #F59E0B  (rankings, numbers)
```

### Typography
```
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
Title:  Inter 700, 28-36px, sentence case
Subtitle: Inter 400, 16-18px, color: #A1A1A1
Numbers: Inter 800, 32-48px
Labels: Inter 500, 16-18px
Source: Inter 400, 11px, color: #555
```

### Layout
- 1080×1080px square
- Padding: 60px all sides
- Clean, minimal — no grid lines, no chart junk
- Bars use solid accent colors, no gradients
- Numbers are the hero — large, bold, prominent

---

## FORMAT 1: RANKED_BARS

Horizontal bar chart. Category labels left, colored bars proportional to value, value number right.

Colors: Amber (#F59E0B) primary, purple (#7C3AED) for top rank.

---

## FORMAT 2: DONUT_BREAKDOWN

Donut chart center. Segments colored with accent + lighter variants. Center shows total or primary stat.

Colors: Purple scale (#7C3AED, #9B6BDF, #B890F3, #D4BFFF).

---

## FORMAT 3: TIMELINE_SHIFT

Horizontal timeline or connected nodes. Each data point = year/period + key stat. Growth arrows or trend indicators.

Colors: Mint (#06D6A0) for positive change, coral (#FF6B6B) for decline.

---

## FORMAT 4: COMPARISON_SPLIT

Split-screen comparison. Two columns with key metrics. Visual divider down center.

Colors: Mint (#06D6A0) vs Coral (#FF6B6B) for contrast. Or Purple vs Amber.

---

## FORMAT 5: HERO_NUMBER

Single massive stat centered (72-96px, Inter 900). Supporting context below. Minimal — let the number dominate.

Colors: White text on dark bg. Accent color for the number.

---

## HTML Template (for all formats)

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1080px; height: 1080px;
    background: #0a0a0a;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #FFFFFF;
    overflow: hidden;
  }
  .container { padding: 60px; height: 100%; }
  .title { font-size: 32px; font-weight: 700; margin-bottom: 8px; }
  .subtitle { font-size: 16px; font-weight: 400; color: #A1A1A1; margin-bottom: 40px; }
  .source { position: absolute; bottom: 40px; left: 60px; font-size: 11px; color: #555; }
  .accent { color: ACCENT_COLOR; }
</style>
</head>
<body>
  <div class="container">
    <!-- format-specific content -->
  </div>
  <div class="source">Source: [source name, year]</div>
</body>
</html>
```

Replace ACCENT_COLOR with the chosen hex value.
