"""Generate a 1024x1024 placeholder app icon (pure stdlib PNG writer).

Produces a violet rounded square with a simple flame glyph — good enough to
build with; replace with a real logo by re-running `npx tauri icon <logo.png>`.
"""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

SIZE = 1024
BG = (26, 26, 31, 255)          # app background
ACCENT = (124, 92, 255, 255)    # violet
GLYPH = (255, 255, 255, 255)


def rounded(x: int, y: int, w: int, h: int, r: int) -> bool:
    if x < r and y < r:
        return (r - x) ** 2 + (r - y) ** 2 <= r * r
    if x > w - r and y < r:
        return (x - (w - r)) ** 2 + (r - y) ** 2 <= r * r
    if x < r and y > h - r:
        return (r - x) ** 2 + (y - (h - r)) ** 2 <= r * r
    if x > w - r and y > h - r:
        return (x - (w - r)) ** 2 + (y - (h - r)) ** 2 <= r * r
    return True


def build() -> bytes:
    cx, cy = SIZE / 2, SIZE / 2
    rows = bytearray()
    for y in range(SIZE):
        rows.append(0)  # filter type 0
        for x in range(SIZE):
            if not rounded(x, y, SIZE, SIZE, 220):
                px = (0, 0, 0, 0)
            else:
                # simple centered "flame": a teardrop-ish blob
                dx, dy = x - cx, y - cy
                flame = (dx / 210) ** 2 + ((dy + 40) / 300) ** 2 <= 1
                tip = dy < -140 and abs(dx) < (dy + 300) / 4
                px = GLYPH if (flame or tip) else ACCENT if 90 < x < SIZE - 90 and 90 < y < SIZE - 90 else BG
            rows.extend(px)
    return bytes(rows)


def chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("icon-source.png")
    ihdr = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(build(), 9)) + chunk(b"IEND", b"")
    out.write_bytes(png)
    print(f"wrote {out} ({len(png)} bytes)")


if __name__ == "__main__":
    main()
