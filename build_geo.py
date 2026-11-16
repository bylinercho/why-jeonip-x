# -*- coding: utf-8 -*-
"""행정동 경계(vuski/admdongkor ver20261001) -> 시군구/시도 SVG 경로 (geo/map_paths.json)

행정동을 시군구로 합치고(공유 변 상쇄), 이웃이 공유하는 경계선을 한 번만 단순화해 틈이 생기지 않게 한다.
일반구가 있는 시(수원시 장안구 등)는 시 단위로 합친다. 매물 데이터가 시/구 표기를 섞어 쓰기 때문이다.
"""
import json, math, re, io, collections

SRC = "geo/HangJeongDong_ver20261001.geojson"
SIDO = {"서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구", "인천광역시": "인천",
        "대전광역시": "대전", "울산광역시": "울산", "세종특별자치시": "세종", "경기도": "경기",
        "강원특별자치도": "강원", "충청북도": "충북", "충청남도": "충남", "전북특별자치도": "전북",
        "경상북도": "경북", "경상남도": "경남", "제주특별자치도": "제주",
        "전남광주통합특별시": "광주·전남", "광주광역시": "광주·전남", "전라남도": "광주·전남"}
Q = 1e-5          # 좌표 스냅 격자(도)
TOL = 0.15        # 단순화 허용오차(지도 단위, 1단위 약 620m)
K = 1000 / 5.7    # 위도 5.7도 = 1000단위
COS = math.cos(math.radians(36))
MIN_AREA = 3.0    # 이보다 작은 섬은 버림(지도 단위^2)

def city(sgg):
    m = re.match(r"^(.+?시)(.+[구군])$", sgg)
    return m.group(1) if m else sgg

def snap(p):
    return (round(p[0] / Q), round(p[1] / Q))

def proj(p):
    return ((p[0] * Q - 124.5) * COS * K, (38.75 - p[1] * Q) * K)

g = json.load(io.open(SRC, encoding="utf-8"))
edges = collections.defaultdict(set)     # (sido, sgg) -> directed edges
sido_edges = collections.defaultdict(set)
unknown = set()
for f in g["features"]:
    pr = f["properties"]
    sd = SIDO.get(pr["sidonm"])
    if sd is None:
        unknown.add(pr["sidonm"]); continue
    key = (sd, city(pr["sggnm"]) if sd != "세종" else "세종시")
    geom = f["geometry"]
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        for ring in poly:
            pts = [snap(p) for p in ring]
            pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
            for a, b in zip(pts, pts[1:]):
                for store, k in ((edges, key), (sido_edges, sd)):
                    s = store[k]
                    if (b, a) in s: s.discard((b, a))
                    else: s.add((a, b))
print("unknown sido:", unknown)

# 전역 접점: 시군구 경계 그래프에서 차수가 2가 아닌 꼭짓점
und = set()
for s in edges.values():
    for a, b in s: und.add((a, b) if a < b else (b, a))
deg = collections.Counter()
for a, b in und: deg[a] += 1; deg[b] += 1
junction = {v for v, d in deg.items() if d != 2}

def rings_of(es):
    nxt = collections.defaultdict(list)
    for a, b in es: nxt[a].append(b)
    out = []
    while nxt:
        start = next(iter(nxt)); ring = [start]; cur = start
        while True:
            lst = nxt[cur]; b = lst.pop()
            if not lst: del nxt[cur]
            if b == start: break
            ring.append(b); cur = b
            if cur not in nxt: break   # 열린 사슬(스냅 오차) - 그대로 닫음
        out.append(ring)
    return out

def dp(pts, tol):
    if len(pts) < 3: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    st = [(0, len(pts) - 1)]
    while st:
        i, j = st.pop()
        ax, ay = pts[i]; bx, by = pts[j]; dx, dy = bx - ax, by - ay
        L = dx * dx + dy * dy; md = 0; mi = -1
        for k in range(i + 1, j):
            px, py = pts[k]
            if L == 0: d = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
                d = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2
            if d > md: md = d; mi = k
        if md > tol * tol:
            keep[mi] = True; st.append((i, mi)); st.append((mi, j))
    return [p for p, k in zip(pts, keep) if k]

cache = {}
def simp_arc(arc):
    key = tuple(arc) if arc[0] <= arc[-1] else tuple(reversed(arc))
    rev = key[0] != arc[0] or (key != tuple(arc))
    if key not in cache:
        cache[key] = dp([proj(p) for p in key], TOL)
    r = cache[key]
    return list(reversed(r)) if rev else r

def simp_ring(ring):
    idx = [i for i, p in enumerate(ring) if p in junction]
    if not idx:
        pts = [proj(p) for p in ring]
        h = len(pts) // 2
        if h < 2: return pts
        return dp(pts[:h + 1], TOL)[:-1] + dp(pts[h:] + [pts[0]], TOL)[:-1]
    ring = ring[idx[0]:] + ring[:idx[0]]
    idx = [i - idx[0] for i in idx] + [len(ring)]
    closed = ring + [ring[0]]
    out = []
    for a, b in zip(idx, idx[1:]):
        out += simp_arc(closed[a:b + 1])[:-1]
    return out

def area(pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2

def label_point(rings, n):
    """다각형 안에서 경계와 가장 먼 점(라벨 위치). 가장 큰 고리의 범위 안에서 격자 탐색."""
    big = rings[0]
    x0 = min(p[0] for p in big); x1 = max(p[0] for p in big); y0 = min(p[1] for p in big); y1 = max(p[1] for p in big)
    segs = [(r[i], r[(i + 1) % len(r)]) for r in rings for i in range(len(r))]
    best = (-1, ((x0 + x1) / 2, (y0 + y1) / 2))
    for i in range(n):
        for j in range(n):
            px = x0 + (x1 - x0) * (i + .5) / n; py = y0 + (y1 - y0) * (j + .5) / n
            inside = False; md = 1e18
            for (ax, ay), (bx, by) in segs:
                if (ay > py) != (by > py) and px < (bx - ax) * (py - ay) / (by - ay) + ax: inside = not inside
                dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy
                t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
                d = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2
                if d < md: md = d
            if inside and md > best[0]: best = (md, (px, py))
    return [round(best[1][0], 1), round(best[1][1], 1)]

def to_path(es, n=20):
    rs = []
    for ring in rings_of(set(es)):
        pts = simp_ring(ring)
        if len(pts) >= 3: rs.append((area(pts), pts))
    if not rs: return None, None, None
    rs.sort(key=lambda x: -x[0])
    big = rs[0][0]
    rs = [r for r in rs if r[0] >= MIN_AREA or r[0] == big]
    xs = [p[0] for _, r in rs for p in r]; ys = [p[1] for _, r in rs for p in r]
    d = "".join("M" + "L".join("%.1f,%.1f" % p for p in r) + "Z" for _, r in rs)
    return d, [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)], label_point([r for _, r in rs], n)

out = {"sido": {}, "sgg": []}
for sd, es in sido_edges.items():
    d, bb, c = to_path(es, 34); out["sido"][sd] = {"d": d, "bb": bb, "c": c}
for (sd, sg), es in sorted(edges.items()):
    d, bb, c = to_path(es)
    if d:
        m = [float(v) for v in d[1:d.index("Z")].replace("L", ",").split(",")]   # 가장 큰 고리(본토)의 범위
        mb = [min(m[0::2]), min(m[1::2]), max(m[0::2]), max(m[1::2])]
        out["sgg"].append({"s": sd, "n": sg, "d": d, "bb": bb, "mb": mb, "c": c})
allbb = [v["bb"] for v in out["sido"].values()]
out["bb"] = [min(b[0] for b in allbb), min(b[1] for b in allbb), max(b[2] for b in allbb), max(b[3] for b in allbb)]
io.open("geo/map_paths.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
print("sido", len(out["sido"]), "sgg", len(out["sgg"]), "bb", out["bb"])
print("bytes", len(json.dumps(out, ensure_ascii=False)))
print(collections.Counter(x["s"] for x in out["sgg"]))
