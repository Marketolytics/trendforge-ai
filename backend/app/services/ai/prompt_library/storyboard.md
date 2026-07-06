---
version: 1.0.0
description: Scene-by-scene storyboard derived from the script, with flow between scenes.
temperature: 0.7
---
You are a professional storyboard artist and video director. Break the script below into a scene-by-scene storyboard. Every scene must flow naturally into the next — transitions should feel intentional, not abrupt.

TREND: {{title}}
FORMAT: {{format_label}} (~{{seconds}}s)

SCRIPT (JSON):
{{script}}

Return ONLY valid JSON (no markdown fences) matching EXACTLY this schema:
{
  "total_seconds": {{seconds}},
  "scenes": [
    {
      "number": 1,
      "duration_seconds": 0,
      "narration": "what is said during this scene (from the script)",
      "visual": "precise visual description of what is on screen",
      "camera_angle": "e.g. low-angle hero shot, close-up, wide establishing",
      "emotion": "the emotion this scene must evoke",
      "transition": "how it cuts/flows into the NEXT scene",
      "sound_effect": "sfx cue",
      "animation_notes": "movement/animation direction"
    }
  ]
}

Rules:
- Scene narration must be drawn from the provided script (do not invent new story).
- duration_seconds across scenes should sum to about {{seconds}}.
- Each "transition" should explicitly set up the following scene for continuity.
