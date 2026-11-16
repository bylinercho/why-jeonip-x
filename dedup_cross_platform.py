# -*- coding: utf-8 -*-
"""플랫폼 간 중복 제거 (4개 플랫폼). 입력은 ../reak, 출력은 현재 폴더(reak_article).
키: 건물(bld_지번키) + 층 + 전용면적(반올림) [+ 보증금 + 월세]
 - 강: 위 키에 가격까지 동일  - 약: 가격 무시(같은 호실 추정)
대표행: 판정 우선순위(불가능>보류>가능>그 외) -> 플랫폼 우선순위(다방>직방>피터팬>당근)
출력: cross_dup_labels.csv, cross_dup_summary.json
"""
import json
import pandas as pd

R = "../reak/"
cols = ["플랫폼", "clean_listing_id", "분석제외_중복", "bld_지번키", "clean_floor",
        "clean_exclusive_area_m2", "clean_deposit_won", "clean_monthly_rent_won"]
d = pd.read_csv(R + "realty_analysis_dataset.csv", encoding="utf-8-sig", low_memory=False, usecols=cols)
l = pd.read_csv(R + "jeonip_labels.csv", encoding="utf-8-sig", usecols=["row_id", "전입판정"])
assert len(d) == len(l)
d["row_id"] = l["row_id"].values
d["판정"] = l["전입판정"].values
ok = (d["분석제외_중복"] == "N") & d["bld_지번키"].notna() & d["clean_floor"].notna() & (d["clean_exclusive_area_m2"] > 0)
x = d[ok].copy()
x["a"] = x["clean_exclusive_area_m2"].round(0)
JP = {"불가능": 0, "보류": 1, "가능": 2}
PP = {"dabang": 0, "zigbang": 1, "peterpan": 2, "daangn": 3}
x["jp"] = x["판정"].map(JP).fillna(3)
x["pp"] = x["플랫폼"].map(PP)

out = []
for tier, keys in [("강", ["bld_지번키", "clean_floor", "a", "clean_deposit_won", "clean_monthly_rent_won"]),
                   ("약", ["bld_지번키", "clean_floor", "a"])]:
    x["gid"] = x.groupby(keys).ngroup()
    n = x.groupby("gid")["플랫폼"].transform("nunique")
    g = x[n > 1].copy()
    g = g.sort_values(["gid", "jp", "pp"])
    g["대표"] = ~g.duplicated("gid")
    g["그룹판정수"] = g.groupby("gid")["판정"].transform("nunique")
    g["티어"] = tier
    out.append(g[["티어", "gid", "플랫폼", "row_id", "clean_listing_id", "판정", "대표", "그룹판정수"]])
o = pd.concat(out)
o.to_csv("cross_dup_labels.csv", index=False, encoding="utf-8-sig")

S = {}
for tier in ["강", "약"]:
    t = o[o["티어"] == tier]
    S[tier] = {"그룹": int(t["gid"].nunique()), "행": int(len(t)), "제거행": int((~t["대표"]).sum()),
               "불가능_제거행": int(((~t["대표"]) & (t["판정"] == "불가능")).sum()),
               "판정충돌_그룹": int((t.groupby("gid")["그룹판정수"].first() > 1).sum()),
               "불가능이_섞인_충돌그룹": int(t.groupby("gid")["판정"].apply(lambda s: ("불가능" in set(s)) and s.nunique() > 1).sum())}
json.dump(S, open("cross_dup_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False, indent=1))
