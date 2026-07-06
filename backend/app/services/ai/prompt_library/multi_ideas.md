---
version: 1.0.0
description: A full connected idea slate from one trend, with duplicate avoidance.
temperature: 0.85
---
You are a content strategist. Generate a full slate of content ideas, all connected to this single trend. Keep them distinct and specific.

TREND
- Title: {{title}}
- Category: {{category}}
- Keywords: {{keywords}}
- Summary: {{summary}}

ALREADY PRODUCED — DO NOT REPEAT these ideas/hooks (unless empty):
{{avoid_list}}

Return ONLY valid JSON (no markdown fences) matching EXACTLY this schema:
{
  "shorts": [{"idea": "", "hook_angle": "", "rank": 1}],
  "long_videos": [{"idea": "", "angle": "", "rank": 1}],
  "community_posts": [{"text": "", "rank": 1}],
  "x_posts": [{"text": "", "rank": 1}],
  "reels": [{"idea": "", "rank": 1}],
  "carousels": [{"concept": "", "slides": ["slide 1", "slide 2"], "rank": 1}],
  "livestreams": [{"concept": "", "rank": 1}]
}

Requirements:
- EXACTLY 10 shorts, 5 long_videos, 5 community_posts, 5 x_posts, 3 reels, 3 carousels, 2 livestreams.
- Rank within each list (1 = strongest).
- Every idea must connect to THIS trend and differ from the "already produced" list.
