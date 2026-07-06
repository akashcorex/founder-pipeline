# Project Context: AI Job Application Autopilot & Co-pilot

Akash's current active product build is an **AI-driven Job Application Assistant** that acts as a precise co-pilot/autopilot for job seekers, matching them to startup roles and submitting highly tailored applications.

## Value Proposition (Precision over Volume)
- **Freshness over scale:** Instantly finding and matching roles posted within the last hour on seed-stage startup career pages rather than applying to week-old stale listings.
- **Filter-proof quality:** Focuses on writing high-quality answers to custom screener questions (often 4-12 questions on visa, salary, prompts) rather than spamming hundreds of generic resumes.
- **Submission Transparency:** Logging exact submitted texts, confirmation IDs, and UI screenshots to build trust with candidates.
- **Outcome Feedback Loop:** tracking which tailoring depths, resume versions, and channels produce response rates to refine the matching logic.

## Technical Architecture (Multi-Agent System)
- **Discovery Agent:** Scrapes, cleans, and normalizes job listings from various boards, career pages, Wellfound, and funding-news feeds into a unified database schema.
- **Matching Agent (RAG-backed):** Embeds the user's profile/resume and the job description, scoring the fit. Retrieves relevant real examples to guide high-quality, non-hallucinated resume tailoring.
- **Execution Agent (ReAct-based):** Fills out complex application forms using an observe-act-adapt loop to dynamically handle unpredictable inputs and screener questions.
- **Orchestrator:** Coordinates the handoffs between discovery, matching, and execution agents; manages rate-limiting, request pacing, and session behavior to minimize bot-detection triggers.

## Engineering Challenges & Realities
- **Anti-Bot Defenses:** Overcoming cloud protection (Cloudflare, DataDome) on target sites like Wellfound, and handling CAPTCHAs on platforms like Greenhouse.
- **Integration Maintenance:** Managing different form layouts and verification loops (Workday review screens, Greenhouse portals, Lever email confirmations).
- **Default Posture:** Defaulting to **Co-pilot Mode** (user previews and approves the resume rewrite and custom answers before submission) to maintain accuracy and build candidate trust, with **Autopilot Mode** (fully unattended) being an explicit opt-in.
- **Repository Strategy:** Keeping the scraping and site-adapter layers isolated as separate deployable boundaries in a monorepo so DOM changes on job boards don't couple to main application deployments.
