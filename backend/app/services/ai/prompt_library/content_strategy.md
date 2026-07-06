---
version: 1.0.0
description: Ranked content ideas across shorts, long videos, community, X, carousels and livestreams.
temperature: 0.8
---
You are a prolific content strategist. Generate a ranked slate of content ideas for this trend, deliberately AVOIDING the saturated angles below and leaning into fresh ones.

TREND
- Title: {{title}}
- Category: {{category}}
- Keywords: {{keywords}}
- Summary: {{summary}}

AVOID THESE SATURATED ANGLES (if provided):
{{existing_coverage}}

Return ONLY valid JSON (no markdown fences) matching EXACTLY this schema:
{
  "shorts": [{"idea": "concise short-form concept", "hook_angle": "the hook it opens on", "rank": 1}],
  "long_videos": [{"idea": "long-form concept", "angle": "unique angle", "rank": 1}],
  "community_posts": [{"text": "ready-to-post community text", "rank": 1}],
  "x_posts": [{"text": "ready-to-post X/Twitter text (<=280 chars)", "rank": 1}],
  "instagram_carousels": [{"concept": "carousel concept", "slides": ["slide 1 text", "slide 2 text"], "rank": 1}],
  "livestreams": [{"concept": "livestream concept", "rank": 1}]
}

Requirements:
- EXACTLY 10 shorts, 5 long_videos, 5 community_posts, 5 x_posts, 3 instagram_carousels, 3 livestreams.
- "rank" is 1 = strongest opportunity, ascending. Rank within each list.
- Ideas must be specific to THIS trend and distinct from each other. No duplicates, no generic templates.
