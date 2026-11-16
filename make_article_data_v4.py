# -*- coding: utf-8 -*-
"""기사용 집계: realty_analysis_dataset.csv + jeonip_labels.csv -> article_numbers.json

주의: 아파트/오피스텔 분류 기준은 reak의 원본 집계 스크립트와 정확히 일치하지 않는다.
(기록상 수치: 본 분석 159,381/1,489, 오피스텔 28,508/3,840, 아파트 63,966/71)
이 스크립트의 재집계치와 차이가 있으면 reak 쪽 분류 기준을 확인해 맞출 것.
"""
import json
import pandas as pd

SIDO_NORM = {
    "서울특별시": "서울", "서울시": "서울", "부산광역시": "부산", "부산시": "부산",
    "대구광역시": "대구", "대구시": "대구", "인천광역시": "인천", "인천시": "인천",
    "대전광역시": "대전", "대전시": "대전", "울산광역시": "울산", "울산시": "울산",
    "세종특별자치시": "세종", "세종시": "세종", "경기도": "경기", "경기": "경기",
    "강원특별자치도": "강원", "강원도": "강원", "충청북도": "충북", "충북": "충북",
    "충청남도": "충남", "충남": "충남", "전북특별자치도": "전북", "전라북도": "전북",
    "경상북도": "경북", "경북": "경북", "경상남도": "경남", "경남": "경남",
    "제주특별자치도": "제주", "제주도": "제주", "제주": "제주",
    "전남광주통합특별시": "광주·전남", "전남광주시": "광주·전남",
    "광주광역시": "광주·전남", "전라남도": "광주·전남",
}

d = pd.read_csv("../reak/realty_analysis_dataset.csv", encoding="utf-8-sig", low_memory=False)
l = pd.read_csv("../reak/jeonip_labels.csv", encoding="utf-8-sig", low_memory=False)
assert (d["플랫폼"].values == l["플랫폼"].values).all()
d["판정"] = l["전입판정"].values
d["지역"] = d["clean_sido"].map(SIDO_NORM).fillna("기타")
d["row_id"] = l["row_id"].values
dd = d[d["분석제외_중복"] == "N"].copy()
n_within = len(dd)
# 플랫폼 간 확실한 중복(건물·층·면적·보증금·월세 동일) 제거: cross_dup_labels.csv(강)의 비대표행
_xd = pd.read_csv("cross_dup_labels.csv", encoding="utf-8-sig")
_rm = _xd[(_xd["티어"] == "강") & (~_xd["대표"])]
_k = set(zip(_rm["플랫폼"], _rm["row_id"]))
dd = dd[[(a, b) not in _k for a, b in zip(dd["플랫폼"], dd["row_id"])]].copy()
print("플랫폼 간 중복 제거:", n_within, "->", len(dd))

def s(c):
    return dd[c].fillna("").astype(str)

# 확정 범위 기준: dabang/daangn=clean_room_type, zigbang/peterpan=clean_building_type
catsrc = s("clean_room_type").where(dd["플랫폼"].isin(["dabang", "daangn"]), s("clean_building_type"))
off = catsrc.str.contains("오피스텔")
apt = catsrc.str.contains("아파트") & ~off
dd["범위"] = "본분석"
dd.loc[off, "범위"] = "오피스텔"
dd.loc[apt, "범위"] = "아파트"
dd["불가"] = dd["판정"].eq("불가능")
dd["보류"] = dd["판정"].eq("보류")

def pack(g):
    return {"n": int(len(g)), "ban": int(g["불가"].sum()),
            "rate": round(float(g["불가"].mean() * 100), 2) if len(g) else 0.0}

out = {"_note": "4플랫폼, 플랫폼 내 확정 중복 + 플랫폼 간 확정 중복(강) 제거", "within_total": int(n_within)}
out["total"] = {**pack(dd), "hold": int(dd["보류"].sum())}
for k in ["아파트", "오피스텔", "본분석"]:
    out[k] = pack(dd[dd["범위"] == k])
out["platform"] = {k: {p: pack(g) for p, g in dd[dd["범위"] == k].groupby("플랫폼")}
                   for k in ["본분석", "오피스텔"]}
out["region"] = {k: {r: pack(g) for r, g in dd[dd["범위"] == k].groupby("지역")}
                 for k in ["본분석", "오피스텔"]}

# 가격 분포: 본 분석 범위 월세 매물
m = dd[(dd["범위"] == "본분석") & (dd["clean_monthly_rent_won"] > 0)].copy()
m["보증금만"] = m["clean_deposit_won"] / 10000
m["월세만"] = m["clean_monthly_rent_won"] / 10000
def price(g):
    return {"n": int(len(g)), "deposit_med": float(g["보증금만"].median()),
            "rent_med": float(g["월세만"].median()),
            "dep_le_1000": round(float((g["보증금만"] <= 1000).mean() * 100), 1),
            "dep_le_3000": round(float((g["보증금만"] <= 3000).mean() * 100), 1)}
out["price"] = {"ban": price(m[m["불가"]]), "ok": price(m[~m["불가"] & ~m["보류"]])}

# 건물 용도 구분(대장)
out["bld_use"] = {str(k): pack(g) for k, g in dd.groupby(dd["bld_용도구분"].fillna("대장없음"))}

# 시군구(일반구가 있는 시는 시 단위)별 집계: [매물, 불가, 비율]
dd["시군구"] = dd["clean_sigungu"].fillna("").astype(str).str.split().str[0]
dd.loc[dd["지역"] == "세종", "시군구"] = "세종시"
sg = {}
for k in ["본분석", "오피스텔"]:
    sg[k] = {}
    for (r, g_), x in dd[(dd["범위"] == k) & dd["시군구"].notna() & (dd["시군구"] != "")].groupby(["지역", "시군구"]):
        sg[k].setdefault(r, {})[g_] = [int(len(x)), int(x["불가"].sum()), round(float(x["불가"].mean() * 100), 2)]
out["sgg"] = sg

# 전입 불가 판정에 걸린 광고 문구 순위(아파트 제외)
ban = dd[dd["불가"] & (dd["범위"] != "아파트")]
ph = l.loc[ban.index, "판정근거"].astype(str).str.extract(r'"([^"]+)"')[0].dropna()
ph = ph.str.replace(r"\s+", " ", regex=True).str.strip()
out["phrases"] = [[k, int(v)] for k, v in ph.value_counts().head(8).items()]
out["phrases_total"] = int(len(ban))

# 보증금 구간 분포(본 분석 범위 월세 매물)
bins = [-1, 100, 300, 500, 1000, 3000, 1e12]
labels = ["100만원 이하", "100~300만원", "300~500만원", "500~1,000만원", "1,000~3,000만원", "3,000만원 초과"]
def dist(g):
    c = pd.cut(g["보증금만"], bins=bins, labels=labels).value_counts(normalize=True)
    return [round(float(c[x] * 100), 1) for x in labels]
out["deposit_dist"] = {"labels": labels, "ban": dist(m[m["불가"]]), "ok": dist(m[~m["불가"] & ~m["보류"]])}

json.dump(out, open("article_numbers_v4.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print({k: out[k] for k in ["phrases","phrases_total","deposit_dist","price"]}); print({k: len(v) for k, v in out["sgg"]["본분석"].items()})


# ===================== 추가 분석 (2026-11-14) =====================
import numpy as np
ext = {}
nonapt = dd[dd["범위"] != "아파트"]
main = dd[dd["범위"] == "본분석"]
mban = main[main["불가"]]
use = main["bld_건축물_주용도"].fillna("")

# (A) 본 분석 전입 불가의 대장 용도 구성 + 지식산업센터(대장 '공장')
def use_group(u):
    if not u: return "대장 없음"
    if "공장" in u: return "공장(지식산업센터 등)"
    f = u.split(" | ")[0]
    if f in ("단독주택", "공동주택"): return "주택(단독·공동)"
    if f == "숙박시설": return "숙박시설"
    if f == "업무시설": return "업무시설"
    if "근린생활시설" in f: return "근린생활시설"
    return "기타"
ug = mban["bld_건축물_주용도"].fillna("").map(use_group).value_counts()
ext["ban_use"] = [[k, int(v)] for k, v in ug.items()]
allug = use.map(use_group)
ext["use_rate"] = {k: pack(main[allug == k]) for k in ug.index}
fac = main[use.str.contains("공장")]
fb = fac[fac["불가"]]
t = fb["clean_title"].fillna("")
ext["factory"] = {**pack(fac), "share_of_ban": round(len(fb) / len(mban) * 100, 1),
                  "buildings": int(fb["bld_지번키"].nunique()), "offices": int(fb["clean_agent_office"].nunique()),
                  "kw_fulloption": int(t.str.contains("풀옵션").sum()), "kw_dorm": int(t.str.contains("기숙사").sum()),
                  "label_room": int(fb["clean_category_label"].fillna("").str.contains("룸").sum()),
                  "top": [[r, g_, int(v)] for (r, g_), v in fb.groupby(["지역", "시군구"]).size().sort_values(ascending=False).head(8).items()]}

# (B) 반복 게시자: 중개사무소별 전입 불가 매물 (아파트 제외). 사무소 이름은 기사용 JSON에 넣지 않는다.
key = nonapt["clean_agent_registration_id"].fillna("").astype(str).str.strip()
key = key.where(key != "", nonapt["clean_agent_office"].fillna("").astype(str).str.strip())
na = nonapt.assign(_k=key)
has = na[na["_k"] != ""]
g = has.groupby("_k").agg(n=("불가", "size"), ban=("불가", "sum"), bld=("bld_지번키", "nunique"),
                          name=("clean_agent_office", "first"), sido=("지역", lambda s: s.mode().iat[0]),
                          sgg=("시군구", lambda s: s.mode().iat[0]))
gb = g[g["ban"] > 0].sort_values("ban", ascending=False)
tot_ban = int(nonapt["불가"].sum())
ext["agents"] = {
    "ban_total": tot_ban, "ban_with_office": int(gb["ban"].sum()), "ban_no_office": tot_ban - int(gb["ban"].sum()),
    "offices_all": int(len(g)), "offices_ban": int(len(gb)),
    "one": int((gb["ban"] == 1).sum()), "ge5": int((gb["ban"] >= 5).sum()), "ge10": int((gb["ban"] >= 10).sum()), "ge20": int((gb["ban"] >= 20).sum()),
    "ban_by_ge10": int(gb.loc[gb["ban"] >= 10, "ban"].sum()),
    "top10_share": round(float(gb["ban"].head(10).sum() / gb["ban"].sum() * 100), 1),
    "top50_share": round(float(gb["ban"].head(50).sum() / gb["ban"].sum() * 100), 1),
    "top100_share": round(float(gb["ban"].head(100).sum() / gb["ban"].sum() * 100), 1),
    "half_ban_offices": int(((gb["ban"] / gb["n"] >= .5) & (gb["n"] >= 10)).sum()),
    "hist": [int((gb["ban"] == 1).sum()), int(gb["ban"].between(2, 4).sum()), int(gb["ban"].between(5, 9).sum()),
             int(gb["ban"].between(10, 19).sum()), int((gb["ban"] >= 20).sum())],
    "top": [{"id": chr(65 + i), "ban": int(r.ban), "n": int(r.n), "share": round(float(r.ban / r.n * 100), 1),
             "bld": int(has[(has["_k"] == k) & has["불가"]]["bld_지번키"].nunique()), "where": r.sido + " " + r.sgg}
            for i, (k, r) in enumerate(gb.head(10).iterrows())]}
gb.head(30).to_csv("agents_top_private_v4.csv", encoding="utf-8-sig")   # 실명 포함, 내부 확인용

# (C) 건물 하나 해부: 전입 불가가 가장 많이 몰린 지번(본 분석 범위)
topkey = mban["bld_지번키"].value_counts().index[0]
B = dd[dd["bld_지번키"] == topkey]
Bb = B[B["불가"]]
ph = l.loc[Bb.index, "판정근거"].astype(str).str.extract(r'"([^"]+)"')[0].dropna().str.strip()
tt = B["clean_title"].fillna("")
ext["building"] = {
    "key": topkey, "name": str(B["bld_건축물_건물명"].mode().iat[0]), "addr": str(B["bld_지번주소"].mode().iat[0]) if "bld_지번주소" in B else "",
    "use": str(B["bld_건축물_주용도"].mode().iat[0]), "use_etc": str(B["bld_건축물_기타용도"].mode().iat[0])[:200],
    "approved": str(B["bld_사용승인일"].mode().iat[0]) if B["bld_사용승인일"].notna().any() else "",
    "n": int(len(B)), "ban": int(len(Bb)), "hold": int(B["보류"].sum()), "ok": int((~B["불가"] & ~B["보류"]).sum()),
    "offices": int(B["clean_agent_office"].nunique()), "offices_ban": int(Bb["clean_agent_office"].nunique()),
    "platform": {k: int(v) for k, v in B["플랫폼"].value_counts().items()},
    "labels": [[k, int(v)] for k, v in B["clean_category_label"].value_counts().head(5).items()],
    "dep_med": float(B["clean_deposit_won"].median() / 10000), "rent_med": float(B["clean_monthly_rent_won"].median() / 10000),
    "area_med": float(B["clean_exclusive_area_m2"].median()),
    "kw": {k: int(tt.str.contains(k).sum()) for k in ["풀옵션", "복층", "스타일러", "발코니", "기숙사", "사업자", "원룸", "주거"]},
    "phrases": [[k, int(v)] for k, v in ph.value_counts().head(6).items()],
    "ok_basis": [[k, int(v)] for k, v in l.loc[B[~B["불가"]].index, "판정방법"].value_counts().items()]}

# (D) 같은 동네·비슷한 면적 월세 비교 (본 분석, 월세 매물, 단기 제외)
r = main[(main["clean_monthly_rent_won"] > 0) & (main["clean_exclusive_area_m2"] > 5) & ~main["보류"]].copy()
r["월세"] = r["clean_monthly_rent_won"] / 10000
r["보증금"] = r["clean_deposit_won"] / 10000
r["면적대"] = pd.cut(r["clean_exclusive_area_m2"], [0, 20, 30, 40, 60, 1e9], labels=["20㎡ 미만", "20~30㎡", "30~40㎡", "40~60㎡", "60㎡ 이상"])
def matched(x, tag):
    cell = x.groupby(["지역", "시군구", "면적대"], observed=True)
    okm = x[~x["불가"]].groupby(["지역", "시군구", "면적대"], observed=True).agg(ok_n=("월세", "size"), ok_rent=("월세", "median"), ok_dep=("보증금", "median"))
    b = x[x["불가"]].join(okm, on=["지역", "시군구", "면적대"])
    b = b[b["ok_n"] >= 20]
    d = b["월세"] - b["ok_rent"]
    return {"tag": tag, "ban_n": int(len(b)), "ban_all": int(x["불가"].sum()), "cells": int(b.groupby(["지역", "시군구", "면적대"], observed=True).ngroups),
            "diff_med": float(d.median()), "diff_q1": float(d.quantile(.25)), "diff_q3": float(d.quantile(.75)),
            "above": round(float((d > 0).mean() * 100), 1), "below": round(float((d < 0).mean() * 100), 1),
            "ban_rent_med": float(b["월세"].median()), "ok_rent_med": float(b["ok_rent"].median()),
            "dep_diff_med": float((b["보증금"] - b["ok_dep"]).median()),
            "hist": [int(v) for v in pd.cut(d, [-1e9, -20, -10, -1e-9, 1e-9, 10, 20, 1e9]).value_counts(sort=False).values]}
resid = r["bld_건축물_주용도"].fillna("").str.split(" | ", regex=False).str[0].isin(["단독주택", "공동주택"])
ext["rent"] = [matched(r, "전체"), matched(r[resid], "대장상 주택만"), matched(r[~resid], "대장상 비주택만")]

out["ext"] = ext
json.dump(out, open("article_numbers_v4.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(ext, ensure_ascii=False, indent=1))
