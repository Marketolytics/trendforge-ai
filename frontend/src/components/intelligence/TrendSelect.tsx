import { useTrends } from "@/store/trends";

interface TrendSelectProps {
  value: number | null;
  onChange: (id: number) => void;
}

/** Dropdown to pick a collected trend for intelligence generators. */
export function TrendSelect({ value, onChange }: TrendSelectProps) {
  const { trends } = useTrends();

  return (
    <select
      value={value ?? ""}
      onChange={(e) => onChange(Number(e.target.value))}
      className="h-9 w-full max-w-md rounded-md border border-[var(--border)] bg-[var(--card)] px-3 text-sm outline-none focus:border-[var(--ring)]"
    >
      <option value="" disabled>
        Select a trend…
      </option>
      {trends.slice(0, 100).map((t) => (
        <option key={t.id} value={t.id}>
          [{Math.round(t.score)}] {t.title.slice(0, 70)}
        </option>
      ))}
    </select>
  );
}
