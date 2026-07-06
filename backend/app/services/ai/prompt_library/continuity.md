---
version: 1.0.0
description: Scene continuity bible — the single source of truth for visual consistency.
temperature: 0.5
---
You are a continuity supervisor. Define ONE consistent visual "bible" for this video so every generated image and video frame keeps the same character, wardrobe, environment and look. These values will be injected verbatim into every scene prompt — be specific and unambiguous.

TREND: {{title}}
FORMAT: {{format_label}}

SCRIPT (JSON):
{{script}}

Return ONLY valid JSON (no markdown fences) matching EXACTLY this schema:
{
  "character_name": "a fixed name/identifier for the main subject",
  "character_appearance": "detailed, fixed physical description (age, build, face, skin, distinguishing features)",
  "clothing": "exact outfit that never changes",
  "hair": "exact hairstyle and color",
  "environment": "the primary setting",
  "time_of_day": "fixed time of day",
  "lighting": "consistent lighting setup",
  "camera_lens": "the lens/focal length used throughout",
  "mood": "overall mood",
  "color_palette": "the fixed palette (name specific colors)",
  "vehicle_position": "if a vehicle is involved, its consistent look/position, else 'n/a'",
  "weather": "consistent weather"
}

Rules:
- Be concrete enough that two different artists would produce the same character.
- If the trend has no human subject, define the consistent mascot/object/scene instead.
