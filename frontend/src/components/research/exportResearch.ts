import type { ResearchAI, ResearchBase } from "@/lib/api";

/** Build a human-readable, PDF-ready Markdown document for a research package. */
export function researchToMarkdown(base: ResearchBase, ai: ResearchAI | null): string {
  const L: string[] = [];
  L.push(`# Research: ${base.title}`, "");
  L.push(`- Research confidence: ${base.research_confidence}/100`);
  L.push(`- Sources: ${base.sources.length} · Cluster: ${base.member_count} items`, "");

  if (ai) {
    L.push("## Executive Summary", "", ai.summaries.executive, "");
    if (ai.key_takeaways.length) {
      L.push("## Key Takeaways", "", ...ai.key_takeaways.map((t) => `- ${t}`), "");
    }
    if (ai.best_creator_angle) L.push("## Best Creator Angle", "", ai.best_creator_angle, "");
  }

  L.push("## Sources", "");
  for (const s of base.sources) L.push(`- **${s.source}** (${s.tier_label}) — ${s.count} item(s)`);
  L.push("");

  L.push("## Timeline", "");
  for (const e of base.timeline) L.push(`- ${e.time ?? "?"} · ${e.source} — ${e.title}`);
  L.push("");

  if (ai) {
    L.push("## Verified Facts", "", ...ai.facts.confirmed.map((f) => `- ${f}`), "");
    if (ai.facts.rumors.length) L.push("## Rumors", "", ...ai.facts.rumors.map((f) => `- ${f}`), "");
    if (ai.verification.possible_misinformation.length)
      L.push("## Possible Misinformation", "", ...ai.verification.possible_misinformation.map((f) => `- ${f}`), "");
    if (ai.outstanding_questions.length)
      L.push("## Outstanding Questions", "", ...ai.outstanding_questions.map((q) => `- ${q}`), "");
  }

  L.push("## Keywords", "", base.keywords.trending.map((k) => k.word).join(", "), "");
  return L.join("\n");
}

export function download(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
