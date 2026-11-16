# -*- coding: utf-8 -*-
"""HTML 본문에 하드코딩돼 있던 수치를 4플랫폼 데이터로 재계산 -> extra_numbers_v4.json
사용: python extra_v4.py [reak폴더=../reak]  (보조 키워드 정의는 이 파일에 명시)"""
import sys, json, re
import pandas as pd
R = (sys.argv[1] if len(sys.argv) > 1 else "../reak").rstrip("/") + "/"
TR = (sys.argv[2] if len(sys.argv) > 2 else R).rstrip("/") + "/"
NOX = len(sys.argv) > 3
d = pd.read_csv(R + "realty_analysis_dataset.csv", encoding="utf-8-sig", low_memory=False, usecols=["플랫폼","clean_listing_id","분석제외_중복","clean_room_type","clean_building_type","bld_조회상태","bld_지번키","bld_건축물_주용도"])
l = pd.read_csv(R + "jeonip_labels.csv", encoding="utf-8-sig", low_memory=False)
d["row_id"] = l["row_id"].values; d["판정"] = l["전입판정"].values
raw_total = int(len(d))
d["matched"] = d["bld_조회상태"].eq("성공")
match = {p: round(float(g["matched"].mean() * 100), 1) for p, g in d.groupby("플랫폼")}
match_nd = {p: round(float(g["matched"].mean() * 100), 1) for p, g in d[d["분석제외_중복"] == "N"].groupby("플랫폼")}
dd = d[d["분석제외_중복"] == "N"].copy()
try:
    if NOX: raise FileNotFoundError
    xd = pd.read_csv("cross_dup_labels.csv", encoding="utf-8-sig")
    rm = xd[(xd["티어"] == "강") & (~xd["대표"])]
    kk = set(zip(rm["플랫폼"], rm["row_id"]))
    dd = dd[[(a, b) not in kk for a, b in zip(dd["플랫폼"], dd["row_id"])]]
except FileNotFoundError:
    pass
s = lambda c: dd[c].fillna("").astype(str)
catsrc = s("clean_room_type").where(dd["플랫폼"].isin(["dabang", "daangn"]), s("clean_building_type"))
off = catsrc.str.contains("오피스텔"); apt = catsrc.str.contains("아파트") & ~off
dd["범위"] = "본분석"; dd.loc[off, "범위"] = "오피스텔"; dd.loc[apt, "범위"] = "아파트"
dd["불가"] = dd["판정"].eq("불가능")
non = dd[dd["범위"] != "아파트"]
u = non["bld_건축물_주용도"].fillna("").astype(str)
first = u.str.split(" | ", regex=False).str[0]
def grp(f, uu):
    if not uu: return "대장없음"
    if "공장" in uu: return "지산"
    if f in ("단독주택", "공동주택"): return "주거용"
    if f == "숙박시설": return "생숙"
    if f == "업무시설": return "오피스텔(업무시설)"
    return "기타 비주거"
g = pd.Series([grp(a, b) for a, b in zip(first, u)], index=non.index)
bt = {k: round(float(non.loc[g == k, "불가"].mean() * 100), 2) for k in g.unique()}
# 오피스텔 불가의 대장 용도
ob = dd[(dd["범위"] == "오피스텔") & dd["불가"]]
f2 = ob["bld_건축물_주용도"].fillna("").astype(str).str.split(" | ", regex=False).str[0]
def comp(f, uu):
    if not uu: return "대장 없음"
    if f == "업무시설": return "업무시설(오피스텔 등)"
    if f == "숙박시설": return "숙박시설(생숙)"
    if f == "공동주택": return "공동주택"
    return "기타"
cc = pd.Series([comp(a, b) for a, b in zip(f2, ob["bld_건축물_주용도"].fillna("").astype(str))], index=ob.index).value_counts()
# 오피스텔 불가 광고 본문 키워드
fin = {"dabang": "dabang_realty_clean_recovered_final.csv", "zigbang": "zigbang_realty_clean_recovered_final.csv",
       "peterpan": "peterpan_realty_clean_recovered_final.csv", "daangn": "daangn_realty_clean_recovered_final.csv"}
texts = []
for p, f in fin.items():
    h = pd.read_csv(TR + f, nrows=0, encoding="utf-8-sig").columns
    tc = next((c for c in ["title", "clean_title"] if c in h), None)
    dc = next((c for c in ["description", "clean_description"] if c in h), None)
    use = [c for c in ["clean_listing_id", tc, dc] if c]
    t = pd.read_csv(TR + f, usecols=use, encoding="utf-8-sig", low_memory=False)
    t["txt"] = (t[tc].fillna("") if tc else "") + " " + (t[dc].fillna("") if dc else "")
    t["플랫폼"] = p
    texts.append(t[["플랫폼", "clean_listing_id", "txt"]])
T = pd.concat(texts)
T["clean_listing_id"] = T["clean_listing_id"].astype(str); ob["clean_listing_id"] = ob["clean_listing_id"].astype(str)
ob = ob.merge(T.drop_duplicates(["플랫폼", "clean_listing_id"]), on=["플랫폼", "clean_listing_id"], how="left")
txt = ob["txt"].fillna("")
APP = r"에어컨|냉장고|세탁기|침대|책상|옷장|풀옵션|인덕션|전자레인지|가전|가구|붙박이|TV|티비|건조기|스타일러"
PET = r"반려|애견|강아지|고양이|펫|애완|동물"
LIV = APP + "|" + PET + r"|신혼|주거|거주|입주|원룸|투룸|복층"
OFC = r"사무|업무|사업자|오피스"
liv = txt.str.contains(LIV); app = txt.str.contains(APP); pet = txt.str.contains(PET)
hints = {"n": int(len(ob)), "live": round(float(liv.mean() * 100), 1), "appliance": round(float(app.mean() * 100), 1),
         "pet": round(float(pet.mean() * 100), 1), "office_only": int((txt.str.contains(OFC) & ~liv).sum())}
main = dd[dd["범위"] == "본분석"]
ur = {}
for k in ["주거용"]:
    sel = non[(g == k) & (non["범위"] == "본분석")]
    ur[k] = {"n": int(len(sel)), "ban": int(sel["불가"].sum())}
out = {"raw_total": raw_total, "match_all": match, "match_nondup": match_nd, "bldtype": bt, "bldtype_n": {k: int((g == k).sum()) for k in g.unique()},
       "comp": {k: int(v) for k, v in cc.items()}, "hints": hints, "after_xdup_rows": int(len(dd))}
json.dump(out, open("extra_numbers_v4.json" if R == "../reak/" else "extra_check.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
