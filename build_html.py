# -*- coding: utf-8 -*-
"""article_src.html + article_numbers.json + geo/map_paths.json
-> 전입신고 불가 매물 추적기_v2.html (단일 파일, 더블클릭으로 열림)"""
import json, io

def load(p):
    return json.dumps(json.load(io.open(p, encoding="utf-8")), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

src = io.open("article_src.html", encoding="utf-8").read()
assert "__DATA__" in src and "__GEO__" in src
out = src.replace("__DATA__", load("article_numbers.json")).replace("__GEO__", load("geo/map_paths.json"))
io.open("전입신고 불가 매물 추적기_v2.html", "w", encoding="utf-8").write(out)
print("ok", len(out.encode("utf-8")))
