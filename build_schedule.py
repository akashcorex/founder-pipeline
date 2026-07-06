#!/usr/bin/env python3
"""
Build schedule.json from pipeline output files.

Reads the generated post text files and media paths, then assembles a
schedule.json that schedule_via_buffer.py can consume.

Usage:
  python3 build_schedule.py [--posts-file linkedin_posts_today.txt]
                            [--ai-news-file ai_news_posts_20260613.txt]
                            [--perf-file performance_posts_20260613.txt]
                            [--carousel-url https://...]
                            [--infographic-url https://...]
                            [--output schedule.json]

If no flags are provided, defaults are used.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta


def parse_write_today_format(text):
    """
    Parse the structured numbered-section post format used by
    generate_posts_via_gemini.py and the agent-driven SKILL.md flow:
    ==================================================
    N. POST TYPE
    ==================================================
    [caption content, may include CAROUSEL CAPTION: or INFOGRAPHIC CAPTION:]
    """
    posts = []
    raw_sections = text.split("==================================================")
    chunks = [s.strip() for s in raw_sections if s.strip()]

    # The delimiter isolates each numbered header ("N. POST TYPE") into its
    # own chunk, separate from the body that follows it, so header and body
    # chunks must be consumed in pairs: [header, body, header, body, ...].
    i = 0
    while i < len(chunks):
        header = chunks[i]
        header_first_word = header.split()[0] if header.split() else ""
        is_header = header_first_word.rstrip(".").isdigit()

        if not is_header:
            i += 1
            continue

        body = chunks[i + 1] if i + 1 < len(chunks) else ""
        i += 2

        post_type = "text"
        header_lower = header.lower()
        if "carousel" in header_lower:
            post_type = "carousel"
        elif "infographic" in header_lower:
            post_type = "infographic"
        elif "poll" in header_lower:
            post_type = "text"

        caption = ""
        media_urls = []

        if "CAROUSEL CAPTION:" in body:
            caption_start = body.index("CAROUSEL CAPTION:") + len("CAROUSEL CAPTION:")
            caption = body[caption_start:].strip()
            if "INFOGRAPHIC CAPTION:" in caption:
                caption = caption.split("INFOGRAPHIC CAPTION:")[0].strip()
        elif "INFOGRAPHIC CAPTION:" in body:
            caption_start = body.index("INFOGRAPHIC CAPTION:") + len(
                "INFOGRAPHIC CAPTION:"
            )
            caption = body[caption_start:].strip()
        elif "CAPTION:" in body:
            caption_start = body.index("CAPTION:") + len("CAPTION:")
            caption = body[caption_start:].strip()
        else:
            clean_lines = []
            for line in body.split("\n"):
                if line.startswith(
                    (
                        "CAROUSEL HOOK",
                        "Slide ",
                        "Chosen ",
                        "Banned ",
                        "Tools/stories",
                        "Source:",
                        "Archetype:",
                        "Why this",
                        "Word count:",
                        "Features:",
                        "Follow @",
                    )
                ):
                    break
                if line.strip():
                    clean_lines.append(line.strip())
            caption = "\n\n".join(clean_lines)

        if caption:
            posts.append(
                {
                    "caption": caption.strip(),
                    "type": post_type,
                    "media_urls": media_urls,
                }
            )

    return posts


def parse_delimited_format(text):
    """
    Parse generic delimited format:
    --- POST ---
    caption text here...
    --- END ---
    """
    posts = []
    blocks = text.split("--- POST ---")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if "--- END ---" in block:
            block = block.split("--- END ---")[0].strip()
        posts.append({"caption": block, "type": "text", "media_urls": []})
    return posts


def parse_plain_text(text):
    """
    Parse plain text: one post per non-empty line, or fallback to whole text as one post.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return []
    posts = []
    for line in lines:
        posts.append({"caption": line, "type": "text", "media_urls": []})
    return posts


def build_schedule(
    reddit_posts,
    ai_news_posts,
    perf_posts,
    carousel_url=None,
    infographic_url=None,
    perf_carousel_url=None,
    perf_infographic_url=None,
    target="linkedin",
):
    """
    Assemble the full 3-day schedule.
    Schedule (IST times):
      Day 1 (today):     9AM Carousel | 12PM Infographic | 3PM Text | 6PM Text
      Day 2 (tomorrow):  9AM-6PM: 4 AI News posts
      Day 3 (day after): 9AM-3PM: 3 AI News posts
    Performance posts get their own slots if available.

    `target` defaults to "linkedin" (this is a LinkedIn-first pipeline, and
    posts are written at LinkedIn length/voice with no separate X-adapted
    copy). Pass target="both" only if you've actually produced distinct,
    X-length copy per the crosspost skill — otherwise the same long-form
    caption gets sent to X as-is and will likely be rejected or truncated.
    """
    today = datetime.now().date()
    schedule_posts = []

    def add_post(
        caption, post_type, day_offset, time_ist, media_urls=None, target=target
    ):
        post_date = (today + timedelta(days=day_offset)).isoformat()
        schedule_posts.append(
            {
                "caption": caption.strip(),
                "type": post_type,
                "date": post_date,
                "time_ist": time_ist,
                "target": target,
                "media_urls": media_urls or [],
                "linkedin_first_comment": "",
            }
        )

    if not reddit_posts and not ai_news_posts and not perf_posts:
        return schedule_posts

    # Day 1: 4 Reddit-based posts
    day1_slots = ["9:00 AM", "12:00 PM", "3:00 PM", "6:00 PM"]
    for idx, post in enumerate(reddit_posts[:4]):
        time_slot = day1_slots[idx] if idx < len(day1_slots) else "9:00 AM"
        media = []
        ptype = post.get("type", "text")

        if ptype == "carousel" and carousel_url:
            media = [carousel_url]
            ptype = "image"
        elif ptype == "infographic" and infographic_url:
            media = [infographic_url]
            ptype = "image"

        add_post(post["caption"], ptype, 0, time_slot, media)

    # Day 2: Next 4 posts (AI news)
    day2_start = len(reddit_posts)
    for idx, post in enumerate(ai_news_posts[:4]):
        time_slot = day1_slots[idx] if idx < len(day1_slots) else "9:00 AM"
        add_post(post["caption"], post.get("type", "text"), 1, time_slot)

    # Day 3: Remaining AI news (up to 3)
    remaining_ai = ai_news_posts[4:7]
    for idx, post in enumerate(remaining_ai):
        time_slot = day1_slots[idx] if idx < len(day1_slots) else "9:00 AM"
        add_post(post["caption"], post.get("type", "text"), 2, time_slot)

    # Performance posts (Day 3 evening or Day 4)
    for idx, post in enumerate(perf_posts):
        time_slot = "6:00 PM" if idx == 0 else "9:00 AM"
        day_offset = 3 if idx == 0 else 4
        add_post(post["caption"], post.get("type", "text"), day_offset, time_slot)

    return schedule_posts


def read_file_safe(path):
    if path and os.path.exists(path):
        with open(path) as f:
            return f.read()
    return ""


def main():
    parser = argparse.ArgumentParser(
        description="Build schedule.json from pipeline output files"
    )
    parser.add_argument(
        "--posts-file",
        default="./linkedin_posts_today.txt",
        help="Reddit-based posts file",
    )
    parser.add_argument("--ai-news-file", default=None, help="AI news posts file")
    parser.add_argument("--perf-file", default=None, help="Performance posts file")
    parser.add_argument(
        "--carousel-url", default=None, help="Public URL for carousel image"
    )
    parser.add_argument(
        "--infographic-url", default=None, help="Public URL for infographic image"
    )
    parser.add_argument(
        "--perf-carousel-url", default=None, help="Public URL for performance carousel"
    )
    parser.add_argument(
        "--perf-infographic-url",
        default=None,
        help="Public URL for performance infographic",
    )
    parser.add_argument(
        "--output", default="./schedule.json", help="Output schedule.json path"
    )
    parser.add_argument(
        "--format",
        default="auto",
        choices=["auto", "writetoday", "delimited", "plain"],
        help="Input format of posts file",
    )
    parser.add_argument(
        "--target",
        default="linkedin",
        choices=["linkedin", "both"],
        help=(
            "Which channel(s) to schedule to (default: linkedin). Only use "
            "'both' if your input already contains distinct, X-length copy "
            "per post \u2014 otherwise the same long-form caption is sent to X "
            "as-is and will likely be rejected or truncated."
        ),
    )

    args = parser.parse_args()

    posts_text = read_file_safe(args.posts_file)
    ai_news_text = read_file_safe(args.ai_news_file) if args.ai_news_file else ""
    perf_text = read_file_safe(args.perf_file) if args.perf_file else ""

    if not posts_text and not ai_news_text and not perf_text:
        print("No input files found. Creating empty schedule template.")
        reddit_posts = []
        ai_news_posts = []
        perf_posts = []
    else:
        fmt = args.format
        if fmt == "auto":
            if "====" in posts_text:
                fmt = "writetoday"
            elif "--- POST ---" in posts_text:
                fmt = "delimited"
            else:
                fmt = "plain"

        if fmt == "writetoday":
            reddit_posts = parse_write_today_format(posts_text) if posts_text else []
        elif fmt == "delimited":
            reddit_posts = parse_delimited_format(posts_text) if posts_text else []
        else:
            reddit_posts = parse_plain_text(posts_text) if posts_text else []

        ai_news_posts = parse_plain_text(ai_news_text) if ai_news_text else []
        perf_posts = parse_plain_text(perf_text) if perf_text else []

    schedule_posts = build_schedule(
        reddit_posts,
        ai_news_posts,
        perf_posts,
        carousel_url=args.carousel_url,
        infographic_url=args.infographic_url,
        perf_carousel_url=args.perf_carousel_url,
        perf_infographic_url=args.perf_infographic_url,
        target=args.target,
    )

    schedule = {"channels": {"linkedin": "", "x": ""}, "posts": schedule_posts}

    with open(args.output, "w") as f:
        json.dump(schedule, f, indent=2)

    print(f"Built schedule.json with {len(schedule_posts)} posts")
    for p in schedule_posts:
        media = " [image]" if p["media_urls"] else ""
        print(
            f"  {p['date']} {p['time_ist']} IST | {p['type']}{media} | {p['caption'][:80]}..."
        )


if __name__ == "__main__":
    main()
