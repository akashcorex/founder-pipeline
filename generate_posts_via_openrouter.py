import os
import json
import urllib.request
import urllib.parse
import ssl
import sys
import datetime
import traceback

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Read Gemini API key from .env
gemini_key = None
env_path = "./.env"
with open(env_path) as f:
    for line in f:
        if line.startswith("GEMINI_API_KEY="):
            gemini_key = line.strip().split("=", 1)[1]
            break

if not gemini_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

# Load Reddit posts data (keep top 15 posts to stay within context limits and keep focus)
reddit_posts = []
if os.path.exists("./reddit_data.json"):
    try:
        with open("./reddit_data.json") as f:
            all_r = json.load(f)
            # Sort by simulated popularity/score or just take top
            reddit_posts = all_r[:15]
    except Exception as e:
        print(f"Error loading reddit_data.json: {e}")

# Load AI News data
ai_news = []
if os.path.exists("./ai_news_data.json"):
    try:
        with open("./ai_news_data.json") as f:
            all_n = json.load(f)
            ai_news = all_n[:12]
    except Exception as e:
        print(f"Error loading ai_news_data.json: {e}")

# Load infographic run-log and calculate banned formats/topics
banned_infographic_formats = []
banned_infographic_topics = []
try:
    if os.path.exists("./infographic-run-log.json"):
        with open("./infographic-run-log.json") as f:
            info_log = json.load(f)
            
        # Last 14 topics are banned
        banned_infographic_topics = [entry["topic"] for entry in info_log[-14:] if "topic" in entry]
        
        # Last 5 formats tally
        recent_formats = [entry["format"] for entry in info_log[-5:] if "format" in entry]
        if recent_formats:
            # Last format is banned
            banned_infographic_formats.append(recent_formats[-1])
            # 3+ times count in last 5 runs
            from collections import Counter
            counts = Counter(recent_formats)
            for fmt, count in counts.items():
                if count >= 3 and fmt not in banned_infographic_formats:
                    banned_infographic_formats.append(fmt)
except Exception as e:
    print(f"Error loading infographic log: {e}")

# Load carousel hook log and calculate banned hook styles
banned_carousel_hooks = []
try:
    if os.path.exists("./carousel-hook-log.json"):
        with open("./carousel-hook-log.json") as f:
            car_log = json.load(f)
            
        recent_hooks = [entry["hook_style"] for entry in car_log[-7:] if "hook_style" in entry]
        if recent_hooks:
            # Last hook is banned
            banned_carousel_hooks.append(recent_hooks[-1])
            # 3+ times count in last 7 runs
            from collections import Counter
            counts = Counter(recent_hooks)
            for hook, count in counts.items():
                if count >= 3 and hook not in banned_carousel_hooks:
                    banned_carousel_hooks.append(hook)
except Exception as e:
    print(f"Error loading carousel log: {e}")

print("Banned Infographic Formats:", banned_infographic_formats)
print("Banned Infographic Topics:", banned_infographic_topics)
print("Banned Carousel Hook Styles:", banned_carousel_hooks)

# Format context strings
reddit_context = ""
for i, post in enumerate(reddit_posts):
    reddit_context += f"Post {i+1} [Subreddit: {post['subreddit']}]:\nTitle: {post['title']}\nContent: {post['selftext'][:400]}...\n---\n"

ai_news_context = ""
for i, item in enumerate(ai_news):
    ai_news_context += f"News {i+1} [Source: {item['source']}]:\nTitle: {item['title']}\nDescription: {item['description'][:400]}...\nURL: {item['url']}\nDate: {item['pubDate']}\n---\n"

system_prompt = """
You are Akash Laha's AI copywriter. Write a daily content batch of exactly 4 posts — Building in Public, Systems/Architecture, Carousel (7 slides + caption), and Infographic (data chart + caption) — based on today's feeds and your knowledge.

IDENTITY: Akash is a full-stack developer working inside a startup while building his own ventures. He documents his journey from developer to technical founder publicly. Every post is first person, sharp, honest, and grounded in real experience. He shares what he's building, what he's learning, what breaks, the systems he studies, and the realities of pursuing ambitious goals.

WRITING RULES:
1. FIRST PERSON ALWAYS. Use "I built", "I learned", "I was wrong about", "I spent [time] on". Never third-person observer voice. Never "we" or generic statements.
2. Sharp, honest, builder-to-builder tone. Like texting another dev who's also trying to ship.
3. Authority earned through specificity. Real numbers, real tradeoffs, real decisions. Never generic claims.
4. No em-dashes anywhere. Use commas, semicolons, or periods.
5. Do NOT include headlines, titles, or headers. Start each post directly with its first sentence/hook.
6. Post structure: Hook (sharp, specific) -> Context (what I was doing) -> Learning/Insight (what went right or wrong) -> Takeaway (what you can use) -> Close (forward-looking, earned).
7. Banned words (NEVER USE ANY): delve, underscore, vibrant, tapestry, interplay, intricate, garner, pivotal, showcase, foster, align with, landscape, key (as adjective), leverages, encompasses, facilitates, utilized, commenced, subsequent to, prior to, in order to, stands as, serves as, is a testament to, plays a vital role, plays a significant role, plays a crucial role, enduring legacy, lasting impact, indelible mark, it's important to note, it's worth noting, no discussion would be complete without, moreover, furthermore, in addition, setting the stage for, marking a shift, evolving landscape, reflects broader trends, game-changer, revolutionary, cutting-edge, mind-blowing, supercharge, unlock, level up, 10x, crushing it, killing it, dominated, so good, changed everything, blew my mind, you won't believe, this is the secret, the one thing, everyone is sleeping on, slept on, the best part?, here's the kicker, and it gets better, but wait there's more, thrilled to share, excited to announce.
8. Banned patterns:
   - "In today's rapidly evolving [anything]"
   - "As a developer, I..." (just say the thing)
   - "I'm excited to share..."
   - "Here's what I learned" (just say what you learned)
   - "What do you think?" / "Agree?" / "Thoughts?"
   - "Drop a comment"
   - LinkedIn-style praise stacking
   - Fake vulnerability ("I was scared to post this")
   - "No X. No Y. Just Z."
   - "It's not just about X. It's about Y."
   - Email sign-off language
9. Varied sentence lengths. Specific numbers over adjectives. No bullets where prose works better.

CONTENT LANES:
- Post 1 (BUILDING IN PUBLIC): What I built, shipped, broke, or learned recently. Real artifact, real outcome. Include specific details — what the code does, what the stack is, what went wrong, what the numbers look like. 800-1500 chars.
- Post 2 (SYSTEMS / ARCHITECTURE): A design decision, tradeoff, or pattern I wrestled with. Include the problem, the options I considered, what I chose, the outcome. Educational but earned — not a tutorial. 800-1500 chars.
- Post 3 (CAROUSEL): A concept worth teaching visually. An architecture pattern, a mental model, a build process, or a framework. 7 slides. Slide 1 hook must follow the chosen hook style from the rotation. 6-8 words max on slide 1. Curiosity gap — never reveal the answer on slide 1.
- Post 4 (INFOGRAPHIC): One striking dataset from the feeds or your knowledge. Data-backed, visual-ready. The caption explains why this data matters and what it means for builders.

OUTPUT FORMAT:
Generate exactly 4 posts using these separators. Do not include any other content.

==================================================
1. BUILDING IN PUBLIC
==================================================
[First person. What I built, shipped, broke, or learned. Real details.]

==================================================
2. SYSTEMS / ARCHITECTURE
==================================================
[Tradeoff, design decision, or pattern. Problem -> options -> choice -> outcome.]

==================================================
3. CAROUSEL
==================================================
CAROUSEL HOOK SELECTION:
  Banned styles: [from hook log]
  Chosen style: [pick from: I Was Wrong, Number Reveal, System Breakdown, Mistake Story, Before/After, Unpopular Opinion, Build Log, Trade-off]
  Hook text: "[6-8 word hook]"

Slide 1:
[Hook following the chosen style. Creates curiosity gap.]

Slide 2:
[The problem or setup. 1-2 sentences.]

Slide 3:
[Concept/principle 1. 1-2 sentences. Specific detail.]

Slide 4:
[Concept/principle 2. 1-2 sentences. Specific detail.]

Slide 5:
[Concept/principle 3. 1-2 sentences. Specific detail.]

Slide 6:
[The insight that ties everything together. 1-2 sentences.]

Slide 7:
[CTA. "Follow @akashlaha for more on [topic]." Nothing else.]

CAROUSEL CAPTION:
[Hook + one sentence summary + close. 4 lines max. No CTA stacking.]

==================================================
4. INFOGRAPHIC
==================================================
Chosen format: [from illustration-formats: RANKED_BARS, DONUT_BREAKDOWN, TIMELINE_SHIFT, COMPARISON_SPLIT, or HERO_NUMBER]
Chosen topic: [one phrase]

INFOGRAPHIC CAPTION:
[Hook stat. Why it matters. What builders should do with this data. Close.]

CRITICAL: Do NOT write any reasoning, chain of thought, drafts, or preamble. Do NOT explain your choices. Only output the final generated posts in the exact format requested. Begin your response directly with '==================================================' and the first post separator.
"""

prompt = f"""
Here are today's feeds for context and inspiration:

REDDIT FEED:
{reddit_context}

AI NEWS FEED:
{ai_news_context}

BANNED CAROUSEL HOOK STYLES (DO NOT USE THESE FOR POST 3 CAROUSEL SLIDE 1):
{', '.join(banned_carousel_hooks) if banned_carousel_hooks else 'None'}
Please select from: I Was Wrong, Number Reveal, System Breakdown, Mistake Story, Before/After, Unpopular Opinion, Build Log, Trade-off.

BANNED INFOGRAPHIC FORMATS (DO NOT USE THESE FOR POST 4):
{', '.join(banned_infographic_formats) if banned_infographic_formats else 'None'}
Please select from: DONUT_BREAKDOWN, TIMELINE_SHIFT, COMPARISON_SPLIT, HERO_NUMBER.

BANNED INFOGRAPHIC TOPICS (DO NOT OVERLAP WITH THESE):
{json.dumps(banned_infographic_topics, indent=2)}

Write the 4 posts now. Remember: first person (I built, I learned), sharp builder voice, no banned words, no engagement bait. The carousel uses Gen Z dark aesthetic. The infographic uses dark mode design. Reference @akashlaha for CTAs.
"""

system_prompt_json = """
You are Akash Laha's AI visual content designer.
Based on the posts generated for today, you must generate structured JSON for the Carousel (Post 3) and Infographic (Post 4) in Gen Z dark aesthetic.

Design system: Dark background (#0a0a0a), bold Inter typography, accent colors: purple (#7C3AED), mint (#06D6A0), coral (#FF6B6B), or amber (#F59E0B). Clean, minimal, no corporate aesthetic.

Output as a single valid JSON object. No markdown code blocks. No text before or after.

{
  "carousel": {
    "format": "[BUILD_LOG, SYSTEM_BREAKDOWN, DATA_STORY, CONTRARIAN_TAKE, FRAMEWORK, or DARK_MINIMAL]",
    "accent_color": "[#7C3AED, #06D6A0, #FF6B6B, or #F59E0B]",
    "hook_style": "[chosen hook style]",
    "slides": [
      { "num": 1, "type": "hook", "headline": "[6-8 word bold hook]", "has_image": false },
      { "num": 2, "type": "context", "headline": "[Problem/setup title]", "body": "[1-2 sentences]", "has_image": true, "image_keyword": "[unsplash search term]" },
      { "num": 3, "type": "point", "headline": "[Point 1 title]", "body": "[1-2 sentences]", "has_image": true, "image_keyword": "[unsplash search term]" },
      { "num": 4, "type": "point", "headline": "[Point 2 title]", "body": "[1-2 sentences]", "has_image": true, "image_keyword": "[unsplash search term]" },
      { "num": 5, "type": "point", "headline": "[Point 3 title]", "body": "[1-2 sentences]", "has_image": true, "image_keyword": "[unsplash search term]" },
      { "num": 6, "type": "insight", "headline": "[Synthesis/tie-together]", "body": "[1-2 sentences]", "has_image": false },
      { "num": 7, "type": "cta", "headline": "Follow @akashlaha for more on [topic]", "has_image": false }
    ]
  },
  "infographic": {
    "format": "[RANKED_BARS, DONUT_BREAKDOWN, TIMELINE_SHIFT, COMPARISON_SPLIT, or HERO_NUMBER]",
    "accent_color": "[#7C3AED, #06D6A0, #FF6B6B, or #F59E0B]",
    "title_main": "[Main title, sentence case]",
    "subtitle": "[One line context, 10-15 words]",
    "source": "[Source name, year]",
    "hero_number": "[If HERO_NUMBER format: big stat]",
    "bars": [
      { "label": "[Category 1]", "value": "[N% or number]", "color": "[accent hex]" },
      { "label": "[Category 2]", "value": "[N% or number]", "color": "[lighter variant]" },
      { "label": "[Category 3]", "value": "[N% or number]", "color": "[lighter variant]" }
    ]
  }
}
"""

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={gemini_key}"
headers = {
    "Content-Type": "application/json"
}

def make_call(system_p, user_p, max_t=4000):
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": user_p
                    }
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {
                    "text": system_p
                }
            ]
        },
        "generationConfig": {
            "maxOutputTokens": max_t
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        print("Calling Google Gemini 3.5 Flash...")
        with urllib.request.urlopen(req, context=ctx) as res:
            resp = json.loads(res.read().decode("utf-8"))
            if resp and isinstance(resp, dict) and "candidates" in resp and len(resp["candidates"]) > 0:
                return resp["candidates"][0]["content"]["parts"][0]["text"]
            else:
                print(f"Gemini returned unexpected response: {resp}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error calling Gemini: {e.code} - {e.reason}")
        try:
            print("Response body:", e.read().decode("utf-8"))
        except Exception as read_err:
            print("Failed to read error body:", read_err)
    except Exception as e:
        traceback.print_exc()
        print(f"Error calling Gemini: {e}")
    return None

# Step 1: Generate LinkedIn text posts
print("Starting Step 1: Generating text posts...")
post_text = make_call(system_prompt, prompt, max_t=4000)

if not post_text:
    print("Error: Failed to generate LinkedIn posts.")
    sys.exit(1)

# Save posts text
date_compact = datetime.date.today().isoformat().replace("-", "")
with open("./linkedin_posts_today.txt", "w") as f:
    f.write(post_text)
with open(f"./linkedin_posts_{date_compact}.txt", "w") as f:
    f.write(post_text)
print(f"Text posts saved to linkedin_posts_{date_compact}.txt")

# Step 2: Extract visuals JSON data based on generated text posts
print("Starting Step 2: Extracting visuals layout JSON...")
json_prompt = f"Here are the generated LinkedIn posts:\n\n{post_text}\n\nGenerate the Carousel and Infographic JSON now."
json_data_str = make_call(system_prompt_json, json_prompt, max_t=2000)

if json_data_str:
    try:
        # Clean up code blocks markdown if LLM wrapped it
        json_data_str = json_data_str.strip()
        if json_data_str.startswith("```json"):
            json_data_str = json_data_str[7:]
        elif json_data_str.startswith("```"):
            json_data_str = json_data_str[3:]
        if json_data_str.endswith("```"):
            json_data_str = json_data_str[:-3]
        json_data_str = json_data_str.strip()
        
        layout_data = json.loads(json_data_str)
        
        # Save carousel_data.json
        with open("./carousel_data.json", "w") as f:
            json.dump(layout_data.get("carousel", {}), f, indent=2)
        print("Saved carousel_data.json")
        
        # Save infographic_data.json
        with open("./infographic_data.json", "w") as f:
            json.dump(layout_data.get("infographic", {}), f, indent=2)
        print("Saved infographic_data.json")
        
    except Exception as e:
        print(f"Error parsing JSON block from response: {e}")
        print("Raw JSON string attempted:")
        print(json_data_str[:1000])
else:
    print("Warning: No JSON data generated in Step 2.")
