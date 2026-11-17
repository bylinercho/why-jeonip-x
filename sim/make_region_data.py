# -*- coding: utf-8 -*-
"""시뮬레이터용 지역 집계: 전입 불가 월세 매물(아파트 제외)의 시·도/시·군·구별 매물 수와 월세 합계.
make_article_data_v4.py와 같은 기준(중복 제거, 범위 분류, 월세 = clean_monthly_rent_won > 0)을 쓴다.
출력: sim/sim_regions.json (개별 매물 정보 없음, 지역별 합계만)"""
import json, pandas as pd
SIDO_NORM = {"서울특별시":"서울","서울시":"서울","부산광역시":"부산","부산시":"부산","대구광역시":"대구","대구시":"대구","인천광역시":"인천","인천시":"인천","대전광역시":"대전","대전시":"대전","울산광역시":"울산","울산시":"울산","세종특별자치시":"세종","세종시":"세종","경기도":"경기","경기":"경기","강원특별자치도":"강원","강원도":"강원","충청북도":"충북","충북":"충북","충청남도":"충남","충남":"충남","전북특별자치도":"전북","전라북도":"전북","경상북도":"경북","경북":"경북","경상남도":"경남","경남":"경남","제주특별자치도":"제주","제주도":"제주","제주":"제주","전남광주통합특별시":"광주·전남","전남광주시":"광주·전남","광주광역시":"광주·전남","전라남도":"광주·전남"}
d=pd.read_csv("../reak/realty_analysis_dataset.csv",encoding="utf-8-sig",low_memory=False)
l=pd.read_csv("../reak/jeonip_labels.csv",encoding="utf-8-sig",low_memory=False)
assert (d["플랫폼"].values==l["플랫폼"].values).all()
d["판정"]=l["전입판정"].values; d["row_id"]=l["row_id"].values
d["지역"]=d["clean_sido"].map(SIDO_NORM).fillna("기타")
dd=d[d["분석제외_중복"]=="N"].copy()
xd=pd.read_csv("cross_dup_labels.csv",encoding="utf-8-sig"); rm=xd[(xd["티어"]=="강")&(~xd["대표"])]
k=set(zip(rm["플랫폼"],rm["row_id"])); dd=dd[[(a,b) not in k for a,b in zip(dd["플랫폼"],dd["row_id"])]].copy()
s=lambda c: dd[c].fillna("").astype(str)
cat=s("clean_room_type").where(dd["플랫폼"].isin(["dabang","daangn"]),s("clean_building_type"))
off=cat.str.contains("오피스텔"); apt=cat.str.contains("아파트")&~off
dd["아파트"]=apt
dd["불가"]=dd["판정"].eq("불가능")
dd["시군구"]=dd["clean_sigungu"].fillna("").astype(str).str.split().str[0]
dd.loc[dd["지역"]=="세종","시군구"]="세종시"
t=dd[dd["불가"]&~dd["아파트"]]
print("전체 불가",int(dd["불가"].sum()),"아파트 불가",int((dd["불가"]&dd["아파트"]).sum()),"전체 매물",len(dd));print("전입 불가(아파트 제외):",len(t),"(기사 수치 9,026과 대조)")
m=t[t["clean_monthly_rent_won"]>0]
print("그중 월세>0:",len(m),"월세합(만원/월):",round(m["clean_monthly_rent_won"].sum()/10000))
out={}
for (r,g),x in m[(m["시군구"]!="")].groupby(["지역","시군구"]):
    out.setdefault(r,{})[g]=[int(len(x)),int(round(x["clean_monthly_rent_won"].sum()/10000))]
nog=m[m["시군구"]==""]
print("시군구 없음:",len(nog))
json.dump(out,open("sim/sim_regions.json","w",encoding="utf-8"),ensure_ascii=False,separators=(",",":"))
print({r:(sum(v[0] for v in g.values()),sum(v[1] for v in g.values())) for r,g in out.items()})
