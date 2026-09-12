"""Extract embedded JSON.parse('...') payloads from a webpack chunk.

Finds every JSON.parse(<string literal>) in the chunk, decodes the JS string
literal, parses it as JSON, and writes each payload to out_dir as NNN.json
with a summary printed at the end.
"""
import json
import sys
from pathlib import Path


def decode_js_string(src: str, start: int):
    """Decode a JS string literal starting at src[start] (a quote char).

    Returns (python_string, index_after_closing_quote).
    """
    quote = src[start]
    assert quote in "'\"`"
    out = []
    i = start + 1
    while i < len(src):
        c = src[i]
        if c == "\\":
            n = src[i + 1]
            if n == "n":
                out.append("\n")
            elif n == "t":
                out.append("\t")
            elif n == "r":
                out.append("\r")
            elif n == "b":
                out.append("\b")
            elif n == "f":
                out.append("\f")
            elif n == "v":
                out.append("\v")
            elif n == "0":
                out.append("\0")
            elif n == "x":
                out.append(chr(int(src[i + 2 : i + 4], 16)))
                i += 4
                continue
            elif n == "u":
                if src[i + 2] == "{":
                    end = src.index("}", i)
                    out.append(chr(int(src[i + 3 : end], 16)))
                    i = end + 1
                    continue
                out.append(chr(int(src[i + 2 : i + 6], 16)))
                i += 6
                continue
            else:
                out.append(n)
            i += 2
            continue
        if c == quote:
            return "".join(out), i + 1
        out.append(c)
        i += 1
    raise ValueError("unterminated string literal")


def main():
    chunk_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    src = chunk_path.read_text(encoding="utf-8")

    needle = "JSON.parse("
    pos = 0
    n = 0
    summary = []
    while True:
        hit = src.find(needle, pos)
        if hit == -1:
            break
        qpos = hit + len(needle)
        if src[qpos] not in "'\"":
            pos = qpos
            continue
        try:
            text, after = decode_js_string(src, qpos)
            data = json.loads(text)
        except Exception as e:
            summary.append((n, hit, "ERROR", str(e)[:80]))
            pos = qpos + 1
            continue
        out_file = out_dir / f"{n:03d}.json"
        out_file.write_text(
            json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8"
        )
        desc = ""
        if isinstance(data, dict):
            desc = "dict keys=" + ",".join(list(data.keys())[:8])
        elif isinstance(data, list):
            desc = f"list len={len(data)}"
            if data and isinstance(data[0], dict):
                desc += " item0 keys=" + ",".join(list(data[0].keys())[:8])
        summary.append((n, hit, f"{len(text)} chars", desc))
        n += 1
        pos = after

    for row in summary:
        print(row)


if __name__ == "__main__":
    main()
