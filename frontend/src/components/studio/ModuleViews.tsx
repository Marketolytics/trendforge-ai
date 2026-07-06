import type {
  BRoll,
  ContinuityBible,
  ImagePrompts,
  ModuleKind,
  ProductionChecklist,
  Script,
  SEOPackage,
  ThumbnailBlueprint,
  VideoPrompts,
  VoiceOver,
} from "@/lib/api";
import { BulletList, Card, CopyButton, Field, Pills } from "./primitives";

/* eslint-disable @typescript-eslint/no-explicit-any */

function ScriptView({ d }: { d: Script }) {
  return (
    <div className="space-y-3">
      <Card>
        <Field label="Hook" value={d.hook} />
      </Card>
      {d.segments?.map((s, i) => (
        <Card key={i}>
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold">{s.label}</p>
            <span className="text-xs text-[var(--muted-foreground)]">{s.seconds}s</span>
          </div>
          <p className="whitespace-pre-wrap text-sm">{s.text}</p>
          {s.retention_marker && (
            <p className="text-xs text-[var(--accent)]">↳ {s.retention_marker}</p>
          )}
        </Card>
      ))}
      <Card>
        <Field label="Climax" value={d.climax} />
        <Field label="CTA" value={d.cta} />
      </Card>
      {d.retention_markers?.length > 0 && (
        <Card>
          <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
            Retention techniques
          </p>
          <Pills items={d.retention_markers} />
        </Card>
      )}
      {d.pacing_notes && (
        <Card>
          <Field label="Pacing" value={d.pacing_notes} />
        </Card>
      )}
    </div>
  );
}

function ContinuityView({ d }: { d: ContinuityBible }) {
  return (
    <Card>
      <div className="grid grid-cols-2 gap-4">
        <Field label="Character" value={d.character_name} />
        <Field label="Hair" value={d.hair} />
        <div className="col-span-2">
          <Field label="Appearance" value={d.character_appearance} />
        </div>
        <Field label="Clothing" value={d.clothing} />
        <Field label="Environment" value={d.environment} />
        <Field label="Time of day" value={d.time_of_day} />
        <Field label="Lighting" value={d.lighting} />
        <Field label="Camera lens" value={d.camera_lens} />
        <Field label="Mood" value={d.mood} />
        <Field label="Color palette" value={d.color_palette} />
        <Field label="Weather" value={d.weather} />
        <Field label="Vehicle" value={d.vehicle_position} />
      </div>
    </Card>
  );
}

function ImagePromptsView({ d }: { d: ImagePrompts }) {
  return (
    <div className="space-y-3">
      {d.character_reference && (
        <Card>
          <Field label="Character reference (locked)" value={d.character_reference} />
        </Card>
      )}
      {d.scenes?.map((s, i) => (
        <Card key={i}>
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold">Scene {s.scene_number}</p>
            <CopyButton text={s.prompt} />
          </div>
          <p className="whitespace-pre-wrap text-sm">{s.prompt}</p>
          {s.consistency_notes && (
            <p className="text-xs text-[var(--accent)]">
              Continuity: {String(s.consistency_notes)}
            </p>
          )}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {s.aspect_ratio && <Pills items={[`AR ${s.aspect_ratio}`]} />}
            {s.style ? <Pills items={[String(s.style)]} /> : null}
          </div>
        </Card>
      ))}
    </div>
  );
}

function VideoPromptsView({ d }: { d: VideoPrompts }) {
  return (
    <div className="space-y-3">
      {d.scenes?.map((s, i) => (
        <Card key={i}>
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold">Scene {s.scene_number}</p>
            <CopyButton text={s.prompt} />
          </div>
          <p className="whitespace-pre-wrap text-sm">{s.prompt}</p>
          {s.continuity_note && (
            <p className="text-xs text-[var(--accent)]">↳ {s.continuity_note}</p>
          )}
          <div className="grid grid-cols-2 gap-2 pt-1 text-xs">
            {(["veo", "runway", "pika", "luma"] as const).map((p) =>
              s[p] ? (
                <div key={p} className="rounded border border-[var(--border)] p-2">
                  <span className="font-semibold uppercase text-[var(--muted-foreground)]">
                    {p}
                  </span>
                  <p className="mt-0.5">{String(s[p])}</p>
                </div>
              ) : null,
            )}
          </div>
        </Card>
      ))}
    </div>
  );
}

function VoiceOverView({ d }: { d: VoiceOver }) {
  return (
    <div className="space-y-3">
      <Card>
        <div className="flex items-center justify-between">
          <Field label="Style" value={d.style} />
          <CopyButton text={d.full_narration} />
        </div>
        <Field label="Full narration" value={d.full_narration} />
      </Card>
      {d.segments?.map((s, i) => (
        <Card key={i}>
          <p className="text-sm">{s.text}</p>
          {s.direction && (
            <p className="text-xs text-[var(--muted-foreground)]">Delivery: {s.direction}</p>
          )}
        </Card>
      ))}
      {d.tips?.length > 0 && (
        <Card>
          <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
            TTS tips
          </p>
          <BulletList items={d.tips} />
        </Card>
      )}
    </div>
  );
}

function BRollView({ d }: { d: BRoll }) {
  return (
    <div className="space-y-2">
      {d.suggestions?.map((s, i) => (
        <Card key={i}>
          <div className="flex items-center gap-2">
            <Pills items={[s.category]} />
            <span className="text-xs text-[var(--muted-foreground)]">{s.timing}</span>
          </div>
          <p className="text-sm">{s.description}</p>
        </Card>
      ))}
    </div>
  );
}

function ThumbnailView({ d }: { d: ThumbnailBlueprint }) {
  return (
    <Card>
      <div className="flex items-center justify-between">
        <div className="inline-flex items-center gap-2 rounded-md border border-[var(--border)] bg-[var(--muted)] px-3 py-1.5">
          <span className="text-[11px] text-[var(--muted-foreground)]">Text</span>
          <span className="text-sm font-semibold uppercase">{d.text}</span>
        </div>
        <span className="text-sm font-semibold text-[var(--success)]">
          {d.ctr_prediction}% CTR
        </span>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Field label="Main subject" value={d.main_subject} />
        <Field label="Emotion" value={d.emotion} />
        <Field label="Background" value={d.background} />
        <Field label="Lighting" value={d.lighting} />
        <Field label="Font style" value={d.font_style} />
        <Field label="Arrows" value={d.arrow_placement} />
        <Field label="Color contrast" value={d.color_contrast} />
      </div>
      {d.highlight_objects?.length > 0 && <Pills items={d.highlight_objects} />}
      <Field label="Notes" value={d.notes} />
    </Card>
  );
}

function SeoView({ d }: { d: SEOPackage }) {
  return (
    <div className="space-y-3">
      <Card>
        <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
          Title variations
        </p>
        <BulletList items={d.title_variations} />
      </Card>
      <Card>
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold">Description</p>
          <CopyButton text={d.description} />
        </div>
        <p className="whitespace-pre-wrap text-sm">{d.description}</p>
      </Card>
      <Card>
        <Field label="Tags" value={undefined} />
        <Pills items={d.tags} />
        <p className="pt-2 text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
          Hashtags
        </p>
        <Pills items={d.hashtags} />
      </Card>
      <Card>
        <Field label="Pinned comment" value={d.pinned_comment} />
        {d.community_poll?.question && (
          <div>
            <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">
              Community poll
            </p>
            <p className="text-sm">{d.community_poll.question}</p>
            <Pills items={d.community_poll.options} />
          </div>
        )}
        <Field label="Playlist" value={d.playlist_recommendation} />
      </Card>
    </div>
  );
}

function ChecklistView({ d }: { d: ProductionChecklist }) {
  return (
    <div className="space-y-3">
      <Card>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Voice over" value={d.voice_over} />
          <Field label="Music style" value={d.music_style} />
          <Field label="Subtitle style" value={d.subtitle_style} />
          <Field label="Thumbnail" value={d.thumbnail} />
        </div>
      </Card>
      <Card>
        <p className="text-sm font-semibold">Visual assets</p>
        <BulletList items={d.visual_assets} />
      </Card>
      <Card>
        <p className="text-sm font-semibold">Sound effects</p>
        <Pills items={d.sound_effects} />
      </Card>
      <Card>
        <p className="text-sm font-semibold">Editing notes</p>
        <BulletList items={d.editing_notes} />
      </Card>
      <Card>
        <p className="text-sm font-semibold">Final review</p>
        <BulletList items={d.final_review} />
      </Card>
    </div>
  );
}

// Registry ------------------------------------------------------------------

export const MODULE_VIEWS: Partial<Record<ModuleKind, (data: any) => JSX.Element>> = {
  script: (d) => <ScriptView d={d} />,
  continuity: (d) => <ContinuityView d={d} />,
  image_prompts: (d) => <ImagePromptsView d={d} />,
  video_prompts: (d) => <VideoPromptsView d={d} />,
  voiceover: (d) => <VoiceOverView d={d} />,
  broll: (d) => <BRollView d={d} />,
  thumbnail_blueprint: (d) => <ThumbnailView d={d} />,
  seo_package: (d) => <SeoView d={d} />,
  checklist: (d) => <ChecklistView d={d} />,
};

export function copyTextFor(kind: ModuleKind, data: any): string {
  if (kind === "script") return data.full_script ?? "";
  if (kind === "voiceover") return data.full_narration ?? "";
  return JSON.stringify(data, null, 2);
}
