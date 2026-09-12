"""CoA Build Hub full archive scraper.

Downloads (politely, ~4 req/s max):
  1. Per-class skill/spell JSON data chunks (22 files)
  2. Icon sprite sheet + CSS
  3. All sitemap pages: guides, static pages
  4. All build pages (sitemap + discovered via listing pagination)
Outputs a structured folder tree under the repo root with raw + parsed data.
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extract_chunk_data import decode_js_string

ROOT = Path(r"C:\Users\Byte\WOW\coabuildhub")
BASE = "https://coabuildhub.com"
DPL = "?dpl=dpl_86r45bT2JRRmtY5dt9n3TVR6zH35"
UA = {"User-Agent": "Mozilla/5.0 (personal archive; contact: site user)"}
DELAY = 0.3

_last = [0.0]


def fetch(url: str) -> bytes:
    wait = DELAY - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
    except Exception as e:
        print(f"  !! {url} -> {e}")
        data = b""
    _last[0] = time.time()
    return data


# ---------------------------------------------------------------- flight
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
        try:
            text, after = decode_js_string(html, q)
        except Exception:
            pos = q + 1
            continue
        parts.append(text)
        pos = after
    return "".join(parts)


def parse_flight_rows(payload: str) -> dict:
    b = payload.encode("utf-8")
    rows = {}
    i = 0
    while i < len(b):
        j = b.find(b":", i)
        if j == -1:
            break
        rid = b[i:j].decode("ascii", "replace")
        if not re.fullmatch(r"[0-9a-f]{1,4}", rid):
            k = b.find(b"\n", i)
            if k == -1:
                break
            i = k + 1
            continue
        if b[j + 1 : j + 2] == b"T":
            k = b.find(b",", j)
            try:
                n = int(b[j + 2 : k].decode(), 16)
            except ValueError:
                i = j + 1
                continue
            rows[rid] = b[k + 1 : k + 1 + n].decode("utf-8", "replace")
            i = k + 1 + n
            if b[i : i + 1] == b"\n":
                i += 1
        else:
            k = b.find(b"\n", j)
            if k == -1:
                k = len(b)
            rows[rid] = b[j + 1 : k].decode("utf-8", "replace")
            i = k + 1
    return rows


def brace_match(s: str, start: int) -> str:
    assert s[start] == "{"
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        c = s[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return s[start : i + 1]
    raise ValueError("unbalanced braces")


def resolve_refs(obj, rows):
    if isinstance(obj, str):
        m = re.fullmatch(r"\$([0-9a-f]{1,4})", obj)
        if m and m.group(1) in rows:
            return rows[m.group(1)]
        return obj
    if isinstance(obj, list):
        return [resolve_refs(x, rows) for x in obj]
    if isinstance(obj, dict):
        return {k: resolve_refs(v, rows) for k, v in obj.items()}
    return obj


# ---------------------------------------------------------------- skills
SKILL_CHUNKS = {
    "barbarian": (2574, "53f92b875df41612"),
    "bloodmage": (3118, "476950969e9745d9"),
    "chronomancer": (2555, "439bb196403984e1"),
    "cultist": (6916, "ee0bdaa0801df6b1"),
    "felsworn": (3842, "1cb3e03f03eade49"),
    "guardian": (2241, "bfec9cda471710bd"),
    "knight-of-xoroth": (9376, "f728f9206efe219c"),
    "manifest": (6589, "0f507342d23bd476"),
    "necromancer": (8916, "47b8c5c3dcf8ba50"),
    "primalist": (769, "899fe94763965155"),
    "pyromancer": (482, "c3f2a3ed60f5a382"),
    "ranger": (1002, "adcfde4e0d4c5fe0"),
    "reaper": (5619, "d41bb20516674551"),
    "runemaster": (8593, "b4d19274bfabb7ab"),
    "starcaller": (4885, "1e7ff19bc41c9173"),
    "stormbringer": (9374, "67f3f2b748e649b3"),
    "sun-cleric": (646, "90fcc22cf0758bd6"),
    "templar": (8084, "c4e62765d3e51b9c"),
    "tinker": (1271, "a03f71eebbe210d7"),
    "venomancer": (7956, "0c23963f918f43e7"),
    "witch-doctor": (4913, "b5798ab503be485a"),
    "witch-hunter": (1194, "725020ecf14f7423"),
}


def all_json_parse_payloads(src: str):
    out = []
    pos = 0
    while True:
        hit = src.find("JSON.parse(", pos)
        if hit == -1:
            break
        q = hit + len("JSON.parse(")
        if src[q] not in "'\"":
            pos = q
            continue
        try:
            text, after = decode_js_string(src, q)
            out.append(json.loads(text))
            pos = after
        except Exception:
            pos = q + 1
    return out


def scrape_skills():
    outdir = ROOT / "skills"
    rawdir = ROOT / "raw" / "chunks" / "skills"
    outdir.mkdir(exist_ok=True)
    rawdir.mkdir(parents=True, exist_ok=True)
    for slug, (chunk_id, h) in SKILL_CHUNKS.items():
        url = f"{BASE}/_next/static/chunks/{chunk_id}.{h}.js{DPL}"
        raw = fetch(url)
        (rawdir / f"{slug}.js").write_bytes(raw)
        payloads = all_json_parse_payloads(raw.decode("utf-8", "replace"))
        data = payloads[0] if len(payloads) == 1 else payloads
        (outdir / f"{slug}.json").write_text(
            json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8"
        )
        n = len(data) if isinstance(data, list) else "?"
        print(f"  skills/{slug}.json ({n} entries)")


def render_skills_md():
    outdir = ROOT / "skills"
    for f in sorted(outdir.glob("*.json")):
        if f.stem == "manifest":
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            continue
        lines = [f"# {f.stem.replace('-', ' ').title()} — Skills & Abilities", ""]
        lines.append(f"Total: {len(data)}")
        for sk in data:
            if not isinstance(sk, dict):
                continue
            name = sk.get("name", "?")
            lines += ["", f"### {name}"]
            scalars = {
                k: v
                for k, v in sk.items()
                if isinstance(v, (str, int, float, bool)) and k not in ("name",)
            }
            meta = " · ".join(f"{k}: {v}" for k, v in scalars.items() if v not in ("", None))
            if meta:
                lines.append(f"*{meta}*")
            for k, v in sk.items():
                if isinstance(v, list) and v:
                    lines.append(f"- **{k}**:")
                    for item in v:
                        if isinstance(item, dict):
                            lines.append(
                                "  - "
                                + "; ".join(f"{a}={b}" for a, b in item.items() if b not in ("", None))
                            )
                        else:
                            lines.append(f"  - {item}")
        f.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
    print("  skills markdown rendered")


# ---------------------------------------------------------------- assets
def scrape_assets():
    adir = ROOT / "assets"
    adir.mkdir(exist_ok=True)
    (adir / "coa-builder-icon.webp").write_bytes(fetch(f"{BASE}/assets/coa-builder-icon.webp"))
    css = (ROOT / "raw" / "coa-icons.css")
    if css.exists():
        (adir / "coa-icons.css").write_bytes(css.read_bytes())
    print("  assets: sprite sheet + css")


# ---------------------------------------------------------------- builds
UUID_RE = re.compile(r"/build/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")


def discover_builds(class_slugs):
    found = set()
    pages = [f"{BASE}/?page={n}" for n in range(1, 15)]
    pages += [f"{BASE}/builds/{s}" for s in class_slugs]
    extra = []
    for url in pages:
        html = fetch(url).decode("utf-8", "replace")
        ids = set(UUID_RE.findall(html))
        new = ids - found
        found |= ids
        # follow pagination links found on class listing pages
        if "/builds/" in url and "?page=" not in url:
            for m in set(re.findall(r"\?page=(\d+)", html)):
                extra.append(f"{url}?page={m}")
        print(f"  listing {url.replace(BASE,'')}: +{len(new)} (total {len(found)})")
    for url in extra:
        html = fetch(url).decode("utf-8", "replace")
        new = set(UUID_RE.findall(html)) - found
        found |= new
        print(f"  listing {url.replace(BASE,'')}: +{len(new)} (total {len(found)})")
    return found


def scrape_build(uuid: str, class_by_id: dict):
    raw_dir = ROOT / "raw" / "builds"
    raw_dir.mkdir(parents=True, exist_ok=True)
    html = fetch(f"{BASE}/build/{uuid}").decode("utf-8", "replace")
    (raw_dir / f"{uuid}.html").write_text(html, encoding="utf-8")
    payload = flight_payload(html)
    rows = parse_flight_rows(payload)
    props = None
    for rid, content in rows.items():
        i = content.find('{"initialBuild":')
        if i != -1:
            try:
                props = json.loads(brace_match(content, i))
            except Exception as e:
                print(f"  !! {uuid}: props parse failed: {e}")
            break
    if props is None:
        print(f"  !! {uuid}: no initialBuild found")
        return None
    props = resolve_refs(props, rows)
    build = props.get("initialBuild", {})
    comments = props.get("initialComments", [])
    similar = props.get("initialSimilar", [])
    cls = class_by_id.get(build.get("class_id"), {})
    slug = cls.get("slug", f"class-{build.get('class_id')}")
    spec = next(
        (s["name"] for s in cls.get("specs", []) if s["id"] == build.get("spec_id")),
        str(build.get("spec_id")),
    )
    bdir = ROOT / "builds" / slug
    bdir.mkdir(parents=True, exist_ok=True)
    out = {"build": build, "comments": comments, "similar": similar,
           "class": cls.get("name"), "spec": spec}
    (bdir / f"{uuid}.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    author = (build.get("author") or {}).get("username") or (build.get("author") or {}).get(
        "display_name", "?"
    )
    md = [
        f"# {build.get('title', uuid)}",
        "",
        f"- **Class/Spec:** {cls.get('name')} — {spec}",
        f"- **Author:** {author}",
        f"- **Role/Type:** {build.get('role')} / {build.get('content_type')}",
        f"- **Tags:** {', '.join(build.get('tags') or [])}",
        f"- **Score:** +{build.get('upvotes', 0)}/-{build.get('downvotes', 0)}"
        f" · {build.get('view_count', 0)} views · {build.get('comment_count', 0)} comments",
        f"- **Updated:** {build.get('updated_at')}",
        f"- **Patch:** {build.get('patch_version')}",
        f"- **URL:** {BASE}/build/{uuid}",
        "",
        f"**Talent string:** `{build.get('talent_string')}`",
        "",
        "---",
        "",
        build.get("description") or "(no guide text)",
    ]
    if comments:
        md += ["", "---", "", "## Comments", ""]
        for c in comments:
            cauthor = (c.get("author") or {}).get("username", "?") if isinstance(c, dict) else "?"
            body = c.get("content", "") if isinstance(c, dict) else str(c)
            md.append(f"**{cauthor}:** {body}")
            md.append("")
    (bdir / f"{uuid}.md").write_text("\n".join(md), encoding="utf-8")
    return build.get("title")


# ---------------------------------------------------------------- pages
def scrape_simple_pages(urls):
    pdir = ROOT / "pages"
    rawdir = ROOT / "raw" / "pages"
    pdir.mkdir(exist_ok=True)
    rawdir.mkdir(parents=True, exist_ok=True)
    for url in urls:
        name = url.rstrip("/").split("/")[-1] or "home"
        html = fetch(url).decode("utf-8", "replace")
        (rawdir / f"{name}.html").write_text(html, encoding="utf-8")
        payload = flight_payload(html)
        rows = parse_flight_rows(payload)
        texts = [v for v in rows.values() if len(v) > 200 and not v.startswith(("I[", "[", "{", "HL["))]
        title = re.search(r"<title>([^<]*)</title>", html)
        md = [f"# {title.group(1) if title else name}", "", f"Source: {url}", ""]
        md += texts
        (pdir / f"{name}.md").write_text("\n\n".join(md), encoding="utf-8")
        print(f"  page {name}: {len(texts)} text blocks")


# ---------------------------------------------------------------- main
def main():
    classes = json.loads((ROOT / "classes.json").read_text(encoding="utf-8"))
    class_by_id = {c["id"]: c for c in classes}
    class_slugs = [c["slug"] for c in classes]

    print("== skills ==")
    scrape_skills()
    render_skills_md()

    print("== assets ==")
    scrape_assets()

    print("== sitemap ==")
    sitemap = fetch(f"{BASE}/sitemap.xml").decode("utf-8", "replace")
    (ROOT / "raw" / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    locs = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    sitemap_builds = {m.group(1) for u in locs if (m := UUID_RE.search(u))}
    guide_urls = [u for u in locs if "/guides/" in u]
    static_urls = [u for u in locs if u.rstrip("/").endswith(("about", "terms", "privacy", "skills"))]

    print("== build discovery ==")
    discovered = discover_builds(class_slugs)
    all_builds = sitemap_builds | discovered
    print(f"  sitemap: {len(sitemap_builds)}, discovered: {len(discovered)}, union: {len(all_builds)}")

    print("== guides & static pages ==")
    scrape_simple_pages(guide_urls + static_urls)

    print(f"== builds ({len(all_builds)}) ==")
    ok = 0
    for n, uuid in enumerate(sorted(all_builds), 1):
        title = scrape_build(uuid, class_by_id)
        if title:
            ok += 1
        if n % 10 == 0:
            print(f"  {n}/{len(all_builds)} done")
    print(f"  builds saved: {ok}/{len(all_builds)}")


if __name__ == "__main__":
    main()
