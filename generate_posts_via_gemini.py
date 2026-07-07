"""
Generates the day's LinkedIn text posts + carousel/infographic layout JSON
by calling Google's Gemini API directly.

Note: despite the historical filename this script used to have
(`generate_posts_via_openrouter.py`), it does NOT call OpenRouter — it calls
`generativelanguage.googleapis.com` with `GEMINI_API_KEY`. `correct_posts.py`
is the script that actually uses OpenRouter (`OPENROUTER_API_KEY`).
"""

import datetime
import json
import os
import time
import sys
import traceback
import urllib.parse
import urllib.request

from env_utils import get_env, new_ssl_context

ctx = new_ssl_context()

gemini_key = get_env("GEMINI_API_KEY")
if not gemini_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

GEMINI_MODELS = [
    "gemini-3.5-flash",
    "gemini-2.0-flash",
]

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
        banned_infographic_topics = [
            entry["topic"] for entry in info_log[-14:] if "topic" in entry
        ]

        # Last 5 formats tally
        recent_formats = [
            entry["format"] for entry in info_log[-5:] if "format" in entry
        ]
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

        recent_hooks = [
            entry["hook_style"] for entry in car_log[-7:] if "hook_style" in entry
        ]
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
    reddit_context += f"Post {i + 1} [Subreddit: {post['subreddit']}]:\nTitle: {post['title']}\nContent: {post['selftext'][:400]}...\n---\n"

ai_news_context = ""
for i, item in enumerate(ai_news):
    ai_news_context += f"News {i + 1} [Source: {item['source']}]:\nTitle: {item['title']}\nDescription: {item['description'][:400]}...\nURL: {item['url']}\nDate: {item['pubDate']}\n---\n"

# Load content doctrine, writing rules, and current project context
content_doctrine = ""
if os.path.exists("./content-doctrine.md"):
    with open("./content-doctrine.md") as f:
        content_doctrine = f.read()

writing_rules = ""
if os.path.exists("./commands/linkedin-content.md"):
    with open("./commands/linkedin-content.md") as f:
        writing_rules = f.read()

project_context = ""
if os.path.exists("./project-context.md"):
    with open("./project-context.md") as f:
        project_context = f.read()

system_prompt = f"""
You are Akash Laha's AI copywriter. Write a daily content batch of exactly 2 posts — Building in Public and Systems/Architecture — based on today's feeds, your knowledge, and our brand guidelines.

==================================================
BRAND DOCTRINE AND BRAND POSITIONING:
==================================================
{content_doctrine}

==================================================
CURRENT VENTURE CONTEXT (WHAT I AM BUILDING):
==================================================
{project_context}

==================================================
WRITING RULES AND SPECIFICATIONS:
==================================================
{writing_rules}

==================================================
OUTPUT FORMAT:
==================================================
Generate exactly 2 posts using these separators. Do not include any other content.

==================================================
1. BUILDING IN PUBLIC
==================================================
[First person. What I built, shipped, broke, or learned about our current venture (the AI Job Application Autopilot/Co-pilot). Ground it in real, specific features, user experiences, or validation metrics from the current venture context.]

==================================================
2. SYSTEMS / ARCHITECTURE
==================================================
[A backend design decision, tradeoff, or pattern I wrestled with for our AI Job Application Autopilot/Co-pilot (e.g., RAG-based resume matching vs free LLM generation, ReAct execution loops for forms, DOM adapter decoupling in the monorepo, or request pacing and concurrency controls to bypass DataDome/Cloudflare). Problem -> options -> choice -> outcome.]

==================================================
CRITICAL: Do NOT write any reasoning, chain of thought, drafts, or preamble. Do NOT explain your choices. Only output the final generated posts in the exact format requested. Begin your response directly with '==================================================' and the first post separator.
"""

prompt = f"""
Here are today's feeds for context and inspiration:

REDDIT FEED:
{reddit_context}

AI NEWS FEED:
{ai_news_context}

BANNED CAROUSEL HOOK STYLES (DO NOT USE THESE FOR POST 3 CAROUSEL SLIDE 1):
{", ".join(banned_carousel_hooks) if banned_carousel_hooks else "None"}
Please select from: I Was Wrong, Number Reveal, System Breakdown, Mistake Story, Before/After, Unpopular Opinion, Build Log, Trade-off.

BANNED INFOGRAPHIC FORMATS (DO NOT USE THESE FOR POST 4):
{", ".join(banned_infographic_formats) if banned_infographic_formats else "None"}
Please select from: DONUT_BREAKDOWN, TIMELINE_SHIFT, COMPARISON_SPLIT, HERO_NUMBER.

BANNED INFOGRAPHIC TOPICS (DO NOT OVERLAP WITH THESE):
{json.dumps(banned_infographic_topics, indent=2)}

Write the 2 posts now. Keep them short, specific, and easy to generate in one pass. Reference @akashlaha only if it fits naturally.
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

headers = {"Content-Type": "application/json"}


def _call_gemini(model_name, system_p, user_p, max_t=4000):
    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_p}]}],
        "systemInstruction": {"parts": [{"text": system_p}]},
        "generationConfig": {"maxOutputTokens": max_t},
    }

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model_name}:generateContent?key={gemini_key}"
    )

    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
    )

    try:
        print(f"Calling Google Gemini model: {model_name}...")
        with urllib.request.urlopen(req, context=ctx, timeout=60) as res:
            resp = json.loads(res.read().decode("utf-8"))
            if (
                resp
                and isinstance(resp, dict)
                and "candidates" in resp
                and len(resp["candidates"]) > 0
            ):
                return resp["candidates"][0]["content"]["parts"][0]["text"]
            else:
                print(f"Gemini returned unexpected response: {resp}")
            return None
    except urllib.error.HTTPError as e:
        print(f"HTTP Error calling Gemini: {e.code} - {e.reason}")
        try:
            print("Response body:", e.read().decode("utf-8"))
        except Exception as read_err:
            print("Failed to read error body:", read_err)
    except urllib.error.URLError as e:
        print(f"URL Error calling Gemini: {e}")
    except Exception as e:
        traceback.print_exc()
        print(f"Error calling Gemini: {e}")
    return None


def make_call(system_p, user_p, max_t=4000, retries=3):
    for model_index, model_name in enumerate(GEMINI_MODELS):
        attempts = retries if model_index == 0 else 1
        for attempt in range(1, attempts + 1):
            print(f"Gemini attempt {attempt}/{attempts} using {model_name}...")
            result = _call_gemini(model_name, system_p, user_p, max_t=max_t)
            if result:
                return result

            if attempt < attempts:
                delay_seconds = 2 ** (attempt - 1)
                print(
                    f"Retrying {model_name} in {delay_seconds}s (attempt {attempt + 1}/{attempts})..."
                )
                time.sleep(delay_seconds)

        if model_index < len(GEMINI_MODELS) - 1:
            print(
                f"Primary Gemini model {model_name} did not respond; trying fallback model {GEMINI_MODELS[model_index + 1]}..."
            )

    return None


def build_fallback_output(reddit_posts, ai_news):
    top_reddit = reddit_posts[0] if reddit_posts else {}
    top_news = ai_news[0] if ai_news else {}

    reddit_title = top_reddit.get("title", "a feed item")
    reddit_source = top_reddit.get("subreddit", "Reddit")
    news_title = top_news.get("title", "an AI news item")
    news_source = top_news.get("source", "AI news")

    post_text = f"""==================================================
1. BUILDING IN PUBLIC
==================================================
I tried to run the daily pipeline live and Gemini hit quota limits again.

Today the fetch layer still recovered from blocked Reddit JSON calls, then the generator fell over on the model call. I am fixing the pipeline so a single upstream failure does not kill the whole schedule.

The useful part is that I can now see the failure boundary clearly. Feed fetch can degrade. Generation needs the same treatment.

==================================================
2. SYSTEMS / ARCHITECTURE
==================================================
I stopped treating Gemini like the only way the pipeline can finish.

The job now has a fallback path: fetch feeds, try Gemini, and if the model is rate-limited or drops the connection, synthesize a deterministic batch from the latest headlines. That keeps the scheduler alive instead of failing at 2 AM because one API is overloaded.

The tradeoff is simple. The fallback batch is less sharp than a model-written one, but it is better than no post at all.
"""

    if reddit_title:
        post_text = post_text.replace("a feed item", reddit_title)
    if reddit_source:
        post_text = post_text.replace(
            "blocked Reddit JSON calls", f"blocked {reddit_source} JSON calls"
        )
    if news_title:
        post_text = post_text.replace("an AI news item", news_title)
    if news_source:
        post_text = post_text.replace("AI news", news_source)

    layout_data = {"carousel": {}, "infographic": {}}
    return post_text, layout_data


# Step 1: Generate LinkedIn text posts
print("Starting Step 1: Generating text posts...")
post_text = make_call(system_prompt, prompt, max_t=8192)

if not post_text:
    print("Gemini failed. Using deterministic fallback draft so the pipeline can continue.")
    post_text, layout_data = build_fallback_output(reddit_posts, ai_news)
else:
    layout_data = None

# Save posts text
date_compact = datetime.date.today().isoformat().replace("-", "")
with open("./linkedin_posts_today.txt", "w") as f:
    f.write(post_text)
with open(f"./linkedin_posts_{date_compact}.txt", "w") as f:
    f.write(post_text)
print(f"Text posts saved to linkedin_posts_{date_compact}.txt")

with open("./carousel_data.json", "w") as f:
    json.dump({}, f)
with open("./infographic_data.json", "w") as f:
    json.dump({}, f)
print("Saved empty carousel_data.json and infographic_data.json")
