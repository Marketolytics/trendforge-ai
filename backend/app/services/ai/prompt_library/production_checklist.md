---
version: 1.0.0
description: End-to-end production checklist for the whole package.
temperature: 0.6
---
You are a producer creating a production checklist so a creator can shoot, edit and publish this video without guesswork.

TREND: {{title}}
FORMAT: {{format_label}} (~{{seconds}}s)

SCRIPT (JSON):
{{script}}

Return ONLY valid JSON (no markdown fences) matching EXACTLY this schema:
{
  "voice_over": "voice-over style + recording notes",
  "visual_assets": ["assets to gather/create"],
  "image_prompts": "note on using the generated image prompts",
  "video_prompts": "note on using the generated video prompts",
  "thumbnail": "thumbnail production note",
  "music_style": "recommended music style/genre + energy",
  "sound_effects": ["key sfx to add"],
  "editing_notes": ["editing directions — cuts, captions, pacing"],
  "subtitle_style": "subtitle/caption style recommendation",
  "final_review": ["final pre-publish review checklist items"]
}

Rules:
- Tailored to the format and this specific trend.
- final_review should be actionable checkboxes.
