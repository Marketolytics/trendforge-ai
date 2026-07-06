import { useRef, type ReactNode } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";

interface VirtualTableProps<T> {
  rows: T[];
  rowHeight?: number;
  height?: number;
  renderRow: (row: T, index: number) => ReactNode;
  header?: ReactNode;
  empty?: ReactNode;
}

/** Windowed list for large datasets — only visible rows are mounted. */
export function VirtualTable<T>({
  rows,
  rowHeight = 56,
  height = 440,
  renderRow,
  header,
  empty,
}: VirtualTableProps<T>) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => rowHeight,
    overscan: 8,
  });

  if (rows.length === 0 && empty) {
    return <>{empty}</>;
  }

  return (
    <div className="surface overflow-hidden">
      {header}
      <div ref={parentRef} className="overflow-y-auto" style={{ height }}>
        <div style={{ height: virtualizer.getTotalSize(), position: "relative" }}>
          {virtualizer.getVirtualItems().map((vi) => (
            <div
              key={vi.key}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: vi.size,
                transform: `translateY(${vi.start}px)`,
              }}
            >
              {renderRow(rows[vi.index], vi.index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
