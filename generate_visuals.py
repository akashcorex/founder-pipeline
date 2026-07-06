#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CAROUSEL_ROUTINE_DIR = os.path.join(PROJECT_ROOT, "carousel-routine")

# Curated high-quality, atmospheric, dark tech developer images on Unsplash
UNSPLASH_FALLBACKS = [
    "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1080&h=1080&fit=crop&q=80",  # Dark 3D shapes
    "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1080&h=1080&fit=crop&q=80",  # VS Code editor
    "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1080&h=1080&fit=crop&q=80",  # Dark laptop code
    "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1080&h=1080&fit=crop&q=80",  # Server racks / network
    "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=1080&h=1080&fit=crop&q=80",  # Terminal / logs
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1080&h=1080&fit=crop&q=80",  # Abstract tech sphere
]

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def generate_carousel_slides(carousel_data):
    if not carousel_data:
        print("No carousel data found. Skipping carousel slide HTML generation.")
        return False

    accent = carousel_data.get("accent_color", "#7C3AED")
    slides = carousel_data.get("slides", [])
    
    # Establish output folders
    temp_dir = os.path.join(CAROUSEL_ROUTINE_DIR, "temp", "carousel-branded")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Clean previous temp slides
    for f in os.listdir(temp_dir):
        if f.startswith("slide-") and f.endswith(".html"):
            os.remove(os.path.join(temp_dir, f))
            
    print(f"Generating {len(slides)} HTML slides in temp/carousel-branded/...")
    
    # Simple radial gradient background themed with the accent color
    glow_color = accent.replace("#", "")
    # Rough conversions for subtle transparent glow
    r_val = int(glow_color[0:2], 16) if len(glow_color) == 6 else 124
    g_val = int(glow_color[2:4], 16) if len(glow_color) == 6 else 58
    b_val = int(glow_color[4:6], 16) if len(glow_color) == 6 else 237

    for idx, slide in enumerate(slides, start=1):
        num_str = f"{idx:02d}"
        headline = slide.get("headline", "")
        body = slide.get("body", "")
        has_image = slide.get("has_image", False)
        
        image_html = ""
        if has_image:
            img_idx = idx % len(UNSPLASH_FALLBACKS)
            img_url = UNSPLASH_FALLBACKS[img_idx]
            image_html = f'''
            <img class="full-bleed-bg" src="{img_url}" alt="slide background">
            <div class="overlay"></div>
            '''
            
        slide_type = slide.get("type", "point")
        content_html = ""
        
        if slide_type == "hook":
            content_html = f'''
            <div class="container" style="justify-content: center; align-items: center; text-align: center; height: 100%;">
              <h1 style="font-size: 60px; font-weight: 900; line-height: 1.15; max-width: 900px; text-transform: uppercase; letter-spacing: -1px;"><span class="accent">{headline}</span></h1>
            </div>
            '''
        elif slide_type == "context":
            content_html = f'''
            <div class="container" style="justify-content: flex-end; height: 100%;">
              {image_html}
              <div class="content" style="background: rgba(13,13,13,0.75); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); padding: 50px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.08); margin-top: auto; box-shadow: 0 20px 50px rgba(0,0,0,0.6);">
                <h2 style="font-size: 38px; font-weight: 800; margin-bottom: 20px;" class="accent">{headline}</h2>
                <p style="font-size: 22px; color: #E5E5E5; line-height: 1.55; font-weight: 400;">{body}</p>
              </div>
            </div>
            '''
        elif slide_type == "cta":
            content_html = f'''
            <div class="container" style="justify-content: center; align-items: center; text-align: center; height: 100%;">
              <div style="background: rgba(17,17,17,0.7); backdrop-filter: blur(16px); padding: 60px; border-radius: 24px; border: 1px solid rgba(255,255,255,0.08); width: 100%; max-width: 800px; box-shadow: 0 20px 40px rgba(0,0,0,0.4);">
                <h1 style="font-size: 42px; font-weight: 800; margin-bottom: 30px; line-height: 1.2; color: #ffffff;">{headline}</h1>
                <div style="height: 3px; width: 60px; background: {accent}; margin: 0 auto 30px auto; border-radius: 2px;"></div>
                <p style="font-size: 20px; color: #A1A1A1; font-weight: 500;">Save this post if you found it useful.</p>
              </div>
            </div>
            '''
        elif slide_type == "insight":
            content_html = f'''
            <div class="container" style="justify-content: center; align-items: center; text-align: center; height: 100%;">
              <div style="max-width: 900px; padding: 40px;">
                <div style="font-size: 18px; font-weight: 800; color: {accent}; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 4px;">The Synthesis</div>
                <h1 style="font-size: 44px; font-weight: 800; line-height: 1.25; color: #ffffff; margin-bottom: 24px;">{headline}</h1>
                <p style="font-size: 22px; color: #CCCCCC; line-height: 1.6; font-style: italic;">{body}</p>
              </div>
            </div>
            '''
        else: # point
            content_html = f'''
            <div class="container" style="justify-content: center; height: 100%;">
              {image_html}
              <div class="content" style="background: rgba(17,17,17,0.85); backdrop-filter: blur(20px); padding: 50px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
                <div style="font-size: 16px; font-weight: 700; color: {accent}; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 3px;">Step 0{idx-2}</div>
                <h2 style="font-size: 40px; font-weight: 800; margin-bottom: 20px; color: #ffffff; line-height: 1.2;">{headline}</h2>
                <p style="font-size: 21px; color: #A1A1A1; line-height: 1.55;">{body}</p>
              </div>
            </div>
            '''

        html_content = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap');
  
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1080px; height: 1080px;
    background: radial-gradient(circle at 80% 20%, rgba({r_val}, {g_val}, {b_val}, 0.12) 0%, #0a0a0a 100%);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #FFFFFF;
    overflow: hidden;
    position: relative;
  }}
  .slide-number {{
    position: absolute; top: 40px; right: 60px;
    font-size: 14px; color: #555;
    font-weight: 600;
    letter-spacing: 1px;
  }}
  .container {{
    padding: 80px 60px 60px 60px;
    height: 100%;
    display: flex;
    flex-direction: column;
  }}
  .accent {{ color: {accent}; }}
  .full-bleed-bg {{
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    object-fit: cover; z-index: -1;
  }}
  .overlay {{
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(180deg, rgba(10,10,10,0.4) 0%, rgba(10,10,10,0.95) 100%); z-index: 0;
  }}
  .content {{ position: relative; z-index: 1; }}
</style>
</head>
<body>
  <div class="slide-number">{num_str} / {len(slides):02d}</div>
  {content_html}
</body>
</html>
'''
        slide_path = os.path.join(temp_dir, f"slide-{num_str}.html")
        with open(slide_path, "w") as f:
            f.write(html_content)
            
    print("Carousel slides successfully written to temp/carousel-branded/")
    return True

def generate_infographic(infographic_data):
    if not infographic_data:
        print("No infographic data found. Skipping infographic HTML generation.")
        return False

    fmt = infographic_data.get("format", "RANKED_BARS")
    accent = infographic_data.get("accent_color", "#06D6A0")
    title = infographic_data.get("title_main", "Data Breakdown")
    subtitle = infographic_data.get("subtitle", "")
    source = infographic_data.get("source", "Internal Study")
    
    chart_html = ""
    
    if fmt == "RANKED_BARS":
        bars = infographic_data.get("bars", [])
        if not bars:
            bars = [
                {"label": "Direct / Database Queries", "value": "45%", "color": accent},
                {"label": "Third Party APIs", "value": "30%", "color": "#1a1a1a"},
                {"label": "Cache / Redis Lookups", "value": "25%", "color": "#1a1a1a"},
            ]
        for bar in bars:
            label = bar.get("label", "")
            val_str = str(bar.get("value", "0"))
            val_pct = val_str.replace("%", "").strip()
            color = bar.get("color", accent)
            if color == "accent" or not color.startswith("#"):
                color = accent
            chart_html += f'''
            <div class="bar-row">
              <div class="bar-label">{label}</div>
              <div class="bar-track">
                <div class="bar-fill" style="width: {val_pct}%; background-color: {color};">
                  <span class="bar-value">{val_str}</span>
                </div>
              </div>
            </div>
            '''
    elif fmt == "DONUT_BREAKDOWN":
        bars = infographic_data.get("bars", [])
        hero_number = infographic_data.get("hero_number", "80%")
        donut_segments = ""
        legend_items = ""
        
        cumulative_pct = 0
        colors = [accent, "#9F7AEA", "#4299E1", "#ED64A6", "#ECC94B"]
        
        for idx, bar in enumerate(bars):
            label = bar.get("label", "")
            val_str = str(bar.get("value", "0"))
            val_pct = float(val_str.replace("%", "").strip())
            color = colors[idx % len(colors)]
            
            # Simple SVG ring dash computation
            dash_array = f"{val_pct} {100 - val_pct}"
            dash_offset = f"{100 - cumulative_pct + 25}"  # Offset start
            donut_segments += f'<circle cx="18" cy="18" r="15.915" fill="none" stroke="{color}" stroke-width="4" stroke-dasharray="{dash_array}" stroke-dashoffset="{dash_offset}"></circle>'
            
            legend_items += f'''
            <div class="legend-item">
              <div class="legend-dot" style="background-color: {color};"></div>
              <span><strong>{val_str}</strong> {label}</span>
            </div>
            '''
            cumulative_pct += val_pct
            
        chart_html = f'''
        <div class="donut-container" style="display: flex; align-items: center; justify-content: center; gap: 60px; height: 100%;">
          <div style="position: relative; width: 340px; height: 340px; display: flex; align-items: center; justify-content: center;">
            <svg width="340" height="340" viewBox="0 0 36 36" style="transform: rotate(-90deg); width: 100%; height: 100%;">
              <circle cx="18" cy="18" r="15.915" fill="none" stroke="#1f1f1f" stroke-width="4"></circle>
              {donut_segments}
            </svg>
            <div class="donut-center" style="position: absolute; text-align: center;">
              <div class="big-number" style="font-size: 64px; font-weight: 800; line-height: 1; color: {accent};">{hero_number}</div>
              <div class="label" style="font-size: 14px; color: #888; margin-top: 8px; max-width: 180px; margin-left: auto; margin-right: auto;">{subtitle}</div>
            </div>
          </div>
          <div class="legend" style="display: flex; flex-direction: column; gap: 16px;">
            {legend_items}
          </div>
        </div>
        '''
    elif fmt == "HERO_NUMBER":
        hero_number = infographic_data.get("hero_number", "99%")
        chart_html = f'''
        <div class="hero" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center;">
          <div class="hero-number" style="font-size: 130px; font-weight: 900; line-height: 1; letter-spacing: -3px; color: {accent}; margin-bottom: 24px;">{hero_number}</div>
          <div class="hero-context" style="font-size: 24px; color: #A1A1A1; max-width: 700px; line-height: 1.6;">{subtitle}</div>
        </div>
        '''
    elif fmt == "TIMELINE_SHIFT":
        # Format expects timeline nodes
        bars = infographic_data.get("bars", [])
        timeline_items = ""
        for bar in bars:
            year = bar.get("label", "2026")
            stat = bar.get("value", "")
            desc = bar.get("desc", "")
            if not desc and ":" in stat:
                stat, _, desc = stat.partition(":")
            timeline_items += f'''
            <div class="timeline-row" style="display: flex; align-items: flex-start; margin-bottom: 30px; gap: 30px;">
              <div class="timeline-year" style="width: 100px; font-size: 32px; font-weight: 800; color: #888888; text-align: right; line-height: 1.1; flex-shrink: 0;">{year}</div>
              <div class="timeline-dot" style="width: 16px; height: 16px; border-radius: 50%; background-color: {accent}; margin-top: 10px; flex-shrink: 0;"></div>
              <div style="flex: 1;">
                <div class="timeline-stat" style="font-size: 24px; font-weight: 700; color: #ffffff; line-height: 1.2;">{stat}</div>
                <div class="timeline-desc" style="font-size: 17px; color: #a1a1a1; margin-top: 4px; line-height: 1.4;">{desc}</div>
              </div>
            </div>
            '''
        chart_html = f'''
        <div style="display: flex; flex-direction: column; justify-content: center; height: 100%; max-width: 800px; margin: 0 auto; padding-top: 40px;">
          {timeline_items}
        </div>
        '''
    elif fmt == "COMPARISON_SPLIT":
        bars = infographic_data.get("bars", [])
        left_label, left_val, left_desc = "Before", "10x", "Manual pipeline efforts"
        right_label, right_val, right_desc = "After", "1s", "Scheduled automation"
        
        if len(bars) >= 2:
            left_label = bars[0].get("label", left_label)
            left_val = bars[0].get("value", left_val)
            left_desc = bars[0].get("desc", left_desc)
            
            right_label = bars[1].get("label", right_label)
            right_val = bars[1].get("value", right_val)
            right_desc = bars[1].get("desc", right_desc)
            
        chart_html = f'''
        <div class="split" style="display: flex; height: 100%; gap: 0; align-items: center; justify-content: center; min-height: 400px;">
          <div class="split-side" style="flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 40px; text-align: center;">
            <div class="split-label" style="font-size: 18px; font-weight: 600; color: #A1A1A1; margin-bottom: 24px; text-transform: uppercase; letter-spacing: 2px;">{left_label}</div>
            <div class="split-number" style="font-size: 80px; font-weight: 900; line-height: 1; margin-bottom: 16px; color: {accent};">{left_val}</div>
            <div class="split-detail" style="font-size: 17px; color: #888888; line-height: 1.5; max-width: 300px; margin: 0 auto;">{left_desc}</div>
          </div>
          <div class="split-divider" style="width: 1px; background: #333333; height: 260px; align-self: center;"></div>
          <div class="split-side" style="flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 40px; text-align: center;">
            <div class="split-label" style="font-size: 18px; font-weight: 600; color: #A1A1A1; margin-bottom: 24px; text-transform: uppercase; letter-spacing: 2px;">{right_label}</div>
            <div class="split-number" style="font-size: 80px; font-weight: 900; line-height: 1; margin-bottom: 16px; color: #ffffff;">{right_val}</div>
            <div class="split-detail" style="font-size: 17px; color: #888888; line-height: 1.5; max-width: 300px; margin: 0 auto;">{right_desc}</div>
          </div>
        </div>
        '''

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: radial-gradient(circle at 50% 50%, #111111 0%, #050505 100%);
    width: 1080px;
    height: 1080px;
    overflow: hidden;
    color: #FFFFFF;
  }}

  .container {{
    width: 1080px;
    height: 1080px;
    padding: 70px 60px 60px 60px;
    display: flex;
    flex-direction: column;
    position: relative;
  }}

  .header {{ margin-bottom: 40px; }}
  .title {{
    font-size: 40px;
    font-weight: 800;
    letter-spacing: -0.8px;
    line-height: 1.25;
    margin-bottom: 10px;
    color: #ffffff;
  }}
  .subtitle {{
    font-size: 18px;
    font-weight: 400;
    color: #888888;
    line-height: 1.5;
  }}

  .chart-area {{ 
    flex: 1; 
    display: flex;
    flex-direction: column;
    justify-content: center;
  }}

  /* Bar chart rules */
  .bar-row {{
    display: flex;
    align-items: center;
    margin-bottom: 16px;
    height: 48px;
  }}
  .bar-label {{
    width: 220px;
    font-size: 16px;
    font-weight: 600;
    color: #CCCCCC;
    text-align: right;
    padding-right: 24px;
    flex-shrink: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}
  .bar-track {{
    flex: 1;
    height: 100%;
    background: #141414;
    border: 1px solid #222222;
    border-radius: 6px;
    overflow: hidden;
    position: relative;
  }}
  .bar-fill {{
    height: 100%;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 16px;
  }}
  .bar-value {{
    font-size: 17px;
    font-weight: 800;
    color: #FFFFFF;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  }}

  .footer {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-top: 30px;
    border-top: 1px solid #1f1f1f;
    padding-top: 20px;
  }}
  .source {{
    font-size: 13px;
    color: #555555;
    font-weight: 500;
  }}
  .brand-tag {{
    font-size: 14px;
    color: #777777;
    font-weight: 700;
    letter-spacing: 0.5px;
  }}
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="title">{title}</div>
      <div class="subtitle">{subtitle}</div>
    </div>
    <div class="chart-area">
      {chart_html}
    </div>
    <div class="footer">
      <div class="source">Source: {source}</div>
      <div class="brand-tag">@akashlaha</div>
    </div>
  </div>
</body>
</html>
'''
    infographic_path = os.path.join(PROJECT_ROOT, "linkedin-infographic.html")
    with open(infographic_path, "w") as f:
        f.write(html_content)
        
    print("Infographic successfully written to ./linkedin-infographic.html")
    return True

def run_rendering_and_logs():
    date_str = datetime.now().strftime("%Y-%m-%d")
    date_compact = datetime.now().strftime("%Y%m%d")
    
    print("\nRunning visual assets rendering...")
    
    # Render Carousel slides to PNGs
    cmd_render = ["node", "render.js", date_str, "carousel-branded"]
    print(f"Running: {' '.join(cmd_render)}")
    subprocess.run(cmd_render, cwd=CAROUSEL_ROUTINE_DIR, check=True)
    
    # Compile Carousel PNGs to PDF
    cmd_pdf = ["node", "render-pdf.js", date_str, "carousel-branded"]
    print(f"Running: {' '.join(cmd_pdf)}")
    subprocess.run(cmd_pdf, cwd=CAROUSEL_ROUTINE_DIR, check=True)
    
    # Capture Infographic PNG
    cmd_capture = [
        "python3", "capture_html.py",
        "--input", "./linkedin-infographic.html",
        "--output", f"./linkedin-infographic-{date_compact}.png",
        "--width", "1080",
        "--height", "1080"
    ]
    print(f"Running: {' '.join(cmd_capture)}")
    subprocess.run(cmd_capture, cwd=PROJECT_ROOT, check=True)
    
    # Update logs
    carousel_data = load_json(os.path.join(PROJECT_ROOT, "carousel_data.json"))
    if carousel_data:
        update_carousel_log(carousel_data, date_str)
        
    infographic_data = load_json(os.path.join(PROJECT_ROOT, "infographic_data.json"))
    if infographic_data:
        update_infographic_log(infographic_data, date_str)

def update_carousel_log(carousel_data, date_str):
    log_path = os.path.join(PROJECT_ROOT, "carousel-hook-log.json")
    try:
        if os.path.exists(log_path):
            with open(log_path) as f:
                log = json.load(f)
        else:
            log = []
    except Exception:
        log = []
        
    slides = carousel_data.get("slides", [])
    hook_text = slides[0].get("headline", "") if slides else ""
    entry = {
        "date": date_str,
        "hook_style": carousel_data.get("hook_style", "UNKNOWN"),
        "hook_text": hook_text,
        "carousel_topic": carousel_data.get("topic", "UNKNOWN"),
        "carousel_format": carousel_data.get("format", "UNKNOWN")
    }
    log.append(entry)
    log = log[-30:]
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
    print(f"Carousel hook log updated: {entry['hook_style']} — {entry['hook_text']}")

def update_infographic_log(infographic_data, date_str):
    log_path = os.path.join(PROJECT_ROOT, "infographic-run-log.json")
    try:
        if os.path.exists(log_path):
            with open(log_path) as f:
                log = json.load(f)
        else:
            log = []
    except Exception:
        log = []
        
    entry = {
        "date": date_str,
        "topic": infographic_data.get("title_main", "UNKNOWN"),
        "format": infographic_data.get("format", "UNKNOWN"),
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }
    log.append(entry)
    log = log[-30:]
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
    print(f"Infographic run-log updated: {entry['topic']} ({entry['format']})")

def main():
    carousel_data = load_json(os.path.join(PROJECT_ROOT, "carousel_data.json"))
    infographic_data = load_json(os.path.join(PROJECT_ROOT, "infographic_data.json"))
    
    if not carousel_data and not infographic_data:
        print("No carousel_data.json or infographic_data.json found. Nothing to generate.")
        sys.exit(1)
        
    generate_carousel_slides(carousel_data)
    generate_infographic(infographic_data)
    run_rendering_and_logs()
    print("\nVisual assets generation and rendering completed successfully!")

if __name__ == "__main__":
    main()
