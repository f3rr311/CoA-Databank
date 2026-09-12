import base64
import json
import zlib
from pathlib import Path

ROOT = Path(r"C:\Users\Byte\WOW\coabuildhub")

# --- skills shape ---
sk = json.load(open(ROOT / "skills" / "barbarian.json", encoding="utf-8"))
print("skills type:", type(sk).__name__)
if isinstance(sk, dict):
    print("keys:", list(sk.keys())[:10])
    k0 = list(sk.keys())[0]
    v = sk[k0]
    print("first val type:", type(v).__name__)
    if isinstance(v, list) and v:
        print("item0:", json.dumps(v[0], ensure_ascii=False)[:800])
elif isinstance(sk, list):
    print("len:", len(sk))
    print("item0:", json.dumps(sk[0], ensure_ascii=False)[:800])

man = json.load(open(ROOT / "skills" / "manifest.json", encoding="utf-8"))
print("\nmanifest type:", type(man).__name__,
      list(man.keys())[:25] if isinstance(man, dict) else len(man))

# --- talent string ---
b = json.load(open(next((ROOT / "builds" / "sun-cleric").glob("*.json")), encoding="utf-8"))
ts = b["build"]["talent_string"]
print("\ntalent_string len:", len(ts), "head:", ts[:60])
pad = ts + "=" * (-len(ts) % 4)
for name, fn in [
    ("b64", lambda s: base64.b64decode(s)),
    ("b64url", lambda s: base64.urlsafe_b64decode(s)),
]:
    try:
        raw = fn(pad)
        print(f"{name}: {len(raw)} bytes, head hex: {raw[:24].hex()}")
        for zname, z in [("zlib", lambda r: zlib.decompress(r)),
                         ("gzip", lambda r: zlib.decompress(r, 31)),
                         ("raw-deflate", lambda r: zlib.decompress(r, -15))]:
            try:
                d = z(raw)
                print(f"  {zname} OK: {len(d)} bytes, head: {d[:80]!r}")
            except Exception:
                pass
        try:
            print("  as json:", json.loads(raw)[:3])
        except Exception:
            pass
        try:
            print("  as text:", raw.decode('utf-8')[:100])
        except Exception:
            pass
        break
    except Exception as e:
        print(f"{name} failed: {e}")
