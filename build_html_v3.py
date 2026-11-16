# -*- coding: utf-8 -*-
"""article_src_v3.html + article_numbers_v4.json(+extra_numbers_v4.json) + geo/map_paths.json -> 전입신고 불가 매물 추적기_v3.html"""
import json, io
def L(p): return json.load(io.open(p, encoding="utf-8"))
def dump(o): return json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
n = L("article_numbers_v4.json"); n["extra"] = L("extra_numbers_v4.json")
src = io.open("article_src_v3.html", encoding="utf-8").read()
out = src.replace("__DATA__", dump(n)).replace("__GEO__", dump(L("geo/map_paths.json")))
io.open("전입신고 불가 매물 추적기_v3.html", "w", encoding="utf-8").write(out)
print("ok", len(out.encode("utf-8")))
