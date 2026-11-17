# -*- coding: utf-8 -*-
"""article_src_v4.html + article_numbers_v4.json(+extra_numbers_v4.json) + geo/map_paths.json -> tracker-v4.html
HTML 수정은 article_src_v4.html에서 하고, 이 스크립트로 tracker-v4.html을 다시 만든다."""
import json, io
def L(p): return json.load(io.open(p, encoding="utf-8"))
def dump(o): return json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", r"<\/")
n = L("article_numbers_v4.json"); n["extra"] = L("extra_numbers_v4.json")
src = io.open("article_src_v4.html", encoding="utf-8", newline="").read()
out = src.replace("__DATA__", dump(n)).replace("__GEO__", dump(L("geo/map_paths.json")))
io.open("tracker-v4.html", "w", encoding="utf-8", newline="").write(out)
print("ok", len(out.encode("utf-8")))
