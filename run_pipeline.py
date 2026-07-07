#!/usr/bin/env python3
"""
run_pipeline.py — one command to run the scriptable parts of the pipeline:
fetch -> generate -> correct -> build schedule -> preview/schedule via Buffer.

By default this is a SAFE DRY RUN: it fetches fresh data, generates posts,
runs the banned-word correction pass, builds schedule.json, and prints
exactly what WOULD be sent to Buffer. Nothing is scheduled live until you
pass --live.

Examples:
  # Preview only (no live posting) — good default for a daily check
  python3 run_pipeline.py

  # Actually schedule the posts to Buffer
  python3 run_pipeline.py --live

  # Reuse already-fetched reddit_data.json / ai_news_data.json
  python3 run_pipeline.py --skip-fetch

  # Skip the OpenRouter banned-word correction pass
  python3 run_pipeline.py --no-correct

  # Attach hosted carousel/infographic images (after rendering + uploading them)
  python3 run_pipeline.py --carousel-url https://... --infographic-url https://...

  # Also cross-post to X (only meaningful if your copy is actually X-length/adapted)
  python3 run_pipeline.py --target both

What this does NOT automate:
  Rendering the carousel (carousel-routine/) and infographic
  (linkedin-infographic-template.html) into actual PNGs is still a
  creative/agent-assisted step (see README.md "Visual Assets" and
  skills/branded-carousel, skills/illustration-formats). generate_posts_via_gemini.py
  produces the copy plus carousel_data.json/infographic_data.json, but turning
  that into on-brand slide art is deliberately not templated here, since the
  point of the branded-carousel/illustration-formats skills is *daily visual
  variety*, which a fixed script would defeat. Render + host those images
  yourself (or via an agent), then pass their URLs with --carousel-url /
  --infographic-url. Without them, those two posts are scheduled as text-only.
"""

import argparse
import json
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REDDIT_DATA_PATH = os.path.join(PROJECT_ROOT, "reddit_data.json")


def step(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def run(cmd, allow_fail=False):
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0 and not allow_fail:
        print(f"\nStep failed: {' '.join(cmd)} (exit {result.returncode})")
        sys.exit(result.returncode)
    return result.returncode


def reddit_data_ok():
    if not os.path.exists(REDDIT_DATA_PATH):
        return False
    try:
        with open(REDDIT_DATA_PATH) as f:
            data = json.load(f)
        return isinstance(data, list) and len(data) > 0
    except Exception:
        return False


def fetch_reddit(py):
    for script in [
        "fetch_reddit_apify.py",
        "fetch_reddit_fallback.py",
        "fetch_reddit_rss.py",
    ]:
        print(f"\nTrying {script}...")
        run([py, script], allow_fail=True)
        if reddit_data_ok():
            print(f"-> {script} produced usable reddit_data.json")
            return True
        print(f"-> {script} did not produce usable data, trying next fallback...")
    print(
        "WARNING: all Reddit fetch methods failed. Continuing without fresh Reddit data."
    )
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Run the full daily LinkedIn content pipeline in one command."
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Reuse existing reddit_data.json / ai_news_data.json instead of re-fetching",
    )
    parser.add_argument(
        "--skip-gen",
        action="store_true",
        help="Skip the Gemini post generation step (useful when the agent writes content directly)",
    )
    parser.add_argument(
        "--no-correct",
        action="store_true",
        help="Skip the OpenRouter banned-word correction pass",
    )
    parser.add_argument(
        "--target",
        default="linkedin",
        choices=["linkedin", "both"],
        help="Where to schedule posts (default: linkedin)",
    )
    parser.add_argument(
        "--carousel-url", default=None, help="Publicly hosted carousel image URL"
    )
    parser.add_argument(
        "--infographic-url", default=None, help="Publicly hosted infographic image URL"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually push the schedule to Buffer (default is a dry-run preview only)",
    )
    args = parser.parse_args()

    py = sys.executable

    if not args.skip_fetch:
        step("STEP 1/5 — Fetching Reddit + AI news")
        fetch_reddit(py)
        run([py, "fetch_ai_news_rss.py"], allow_fail=True)
    else:
        step("STEP 1/5 — Skipped (--skip-fetch)")

    if not args.skip_gen:
        step("STEP 2/5 — Generating posts (Gemini)")
        run([py, "generate_posts_via_gemini.py"])
    else:
        step("STEP 2/5 — Skipped post generation (--skip-gen)")

    step("STEP 2.5/5 — Generating and rendering visual assets (Puppeteer)")
    run([py, "generate_visuals.py"])

    if not args.no_correct:
        step("STEP 3/5 — Correcting banned words (OpenRouter)")
        rc = run([py, "correct_posts.py"], allow_fail=True)
        if rc != 0:
            print(
                "Correction pass failed or OPENROUTER_API_KEY is missing; continuing with uncorrected posts."
            )
    else:
        step("STEP 3/5 — Skipped (--no-correct)")

    step("STEP 4/5 — Building schedule.json")
    build_cmd = [py, "build_schedule.py", "--target", args.target]
    if args.carousel_url:
        build_cmd += ["--carousel-url", args.carousel_url]
    if args.infographic_url:
        build_cmd += ["--infographic-url", args.infographic_url]
    run(build_cmd)

    if not args.carousel_url or not args.infographic_url:
        print(
            "\nNote: no --carousel-url/--infographic-url supplied, so the carousel and/or "
            "infographic post(s) will be scheduled as TEXT ONLY (caption, no image). "
            "Rendering on-brand visuals is still a separate step — see README.md 'Visual Assets'."
        )

    step("STEP 5/5 — Buffer: dry-run preview")
    run([py, "schedule_via_buffer.py", "--schedule-file", "schedule.json", "--dry-run"])

    if args.live:
        step("LIVE — Scheduling to Buffer")
        run([py, "schedule_via_buffer.py", "--schedule-file", "schedule.json"])
        print("\nDone. Posts scheduled to Buffer.")
    else:
        print(
            "\nDry run complete. Nothing was posted. Re-run with --live to actually schedule these posts to Buffer."
        )


if __name__ == "__main__":
    main()
