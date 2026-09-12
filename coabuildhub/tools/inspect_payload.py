import json
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
print("top keys:", list(d.keys()))
k = list(d.keys())[0]
v = d[k]
print(f"type of d[{k}]:", type(v).__name__)
if isinstance(v, dict):
    print("keys:", list(v.keys())[:20])
    for kk, vv in list(v.items())[:6]:
        if isinstance(vv, dict):
            print(" ", kk, "dict", list(vv.keys())[:12])
        elif isinstance(vv, list):
            print(" ", kk, "list len", len(vv))
            if vv and isinstance(vv[0], dict):
                print("    item0:", json.dumps(vv[0], ensure_ascii=False)[:600])
        else:
            print(" ", kk, repr(vv)[:200])
elif isinstance(v, list):
    print("len:", len(v))
    print(json.dumps(v[0], indent=1, ensure_ascii=False)[:1500])
