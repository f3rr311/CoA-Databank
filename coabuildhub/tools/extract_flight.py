"""Extract the Next.js RSC flight payload from a page's HTML.

Collects every self.__next_f.push([1,"..."]) fragment, decodes the JS string
literals, joins them, and writes the combined payload. Also tries to locate
and pretty-print embedded JSON objects of interest (build data).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extract_chunk_data import decode_js_string


def flight_payload(html: str) -> str:
    parts = []
    needle = "self.__next_f.push([1,"
    pos = 0
    while True:
        hit = html.find(needle, pos)
        if hit == -1:
            break
        q = hit + len(needle)
        if html[q] not in "'\"":
            pos = q
            continue
        text, after = decode_js_string(html, q)
        parts.append(text)
        pos = after
    return "".join(parts)


def main():
    html = Path(sys.argv[1]).read_text(encoding="utf-8")
    out = Path(sys.argv[2])
    payload = flight_payload(html)
    out.write_text(payload, encoding="utf-8")
    print(f"payload: {len(payload)} chars -> {out}")
    # show the line-keys of the flight stream
    for line in payload.split("\n"):
        if not line:
            continue
        key = line.split(":", 1)[0]
        rest = line.split(":", 1)[1] if ":" in line else ""
        print(f"  {key}: {rest[:120]!r}")


if __name__ == "__main__":
    main()
