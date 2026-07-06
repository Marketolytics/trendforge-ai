/** Human-friendly relative time, e.g. "3h ago". */
export function relativeTime(iso: string | null | undefined): string {
  if (!iso) return "unknown";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "unknown";
  const seconds = Math.round((Date.now() - then) / 1000);

  if (seconds < 45) return "just now";
  const units: [number, string][] = [
    [60, "s"],
    [60, "m"],
    [24, "h"],
    [7, "d"],
    [4.3, "w"],
    [12, "mo"],
  ];
  let value = seconds;
  let unit = "s";
  for (let i = 0; i < units.length; i++) {
    const [size, label] = units[i];
    if (value < size) {
      unit = label;
      break;
    }
    value = Math.floor(value / size);
    unit = units[i + 1] ? units[i + 1][1] : "y";
  }
  return `${value}${unit} ago`;
}

/** Format a score (0-100) with no decimals when whole. */
export function formatScore(score: number): string {
  return Number.isInteger(score) ? String(score) : score.toFixed(1);
}

/** Compact number formatting, e.g. 133205 -> "133K". */
export function compactNumber(n: number | null | undefined): string {
  if (n == null) return "—";
  if (n < 1000) return String(n);
  if (n < 1_000_000) return `${(n / 1000).toFixed(n < 10_000 ? 1 : 0)}K`;
  return `${(n / 1_000_000).toFixed(1)}M`;
}
