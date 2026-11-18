# -*- coding: utf-8 -*-
"""원본 시뮬레이터(potential_tax_simulator_12 (1).html)를 전국 데이터·1주택 비과세 반영 버전으로 변환해 simulator.html 생성"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / "potential_tax_simulator_12 (1).html").read_text(encoding="utf-8")
reg = (ROOT / "sim" / "sim_regions.json").read_text(encoding="utf-8")
s = src


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:60])
    s = s.replace(a, b)


# ---------- 제목·설명 ----------
rep("<title>전입신고 불가 월세 매물 잠재세수 시뮬레이터</title>", "<title>전입신고 불가 월세 매물 잠재세수 시뮬레이터 (전국)</title>")
rep("""<p class="sub">크롤링한 매물 데이터와 여러 가정값을 바탕으로, 해당 임대소득이 정상적으로 신고·과세될 경우 발생할 수 있는 <b>잠재 세수 규모</b>를 추정합니다.</p>""",
    """<p class="sub">2026년 11월 다방·직방·피터팬·당근마켓에서 모은 전국 매물 가운데, 광고에 전입신고 불가를 밝힌 <b>월세 매물 8,924건</b>(아파트 제외)의 임대소득이 정상적으로 신고·과세될 경우 발생할 수 있는 <b>잠재 세수 규모</b>를 추정합니다.</p>""")
rep("""실제 임대인별 세부담과는 다를 수 있습니다.""",
    """광고에 전입신고 불가를 적은 매물이 곧 세금을 내지 않는 매물이라는 뜻은 아니며, 실제 임대인별 세부담과는 다를 수 있습니다. 기본 가정값은 근거가 확인된 통계가 아니라 예시입니다.""")

# ---------- CSS: 지역 그룹 ----------
rep("  #bracketWrap { margin-top: 12px; }", """  .region-group { border: 1px solid var(--border); border-radius: 10px; margin-bottom: 8px; background: var(--page); }
  .rg-head { display: flex; align-items: center; gap: 10px; padding: 8px 12px; flex-wrap: wrap; }
  .rg-head label { display: flex; align-items: center; gap: 7px; font-size: 13.5px; font-weight: 600; cursor: pointer; flex: 1 1 auto; min-width: 140px; }
  .rg-head input[type="checkbox"] { width: 15px; height: 15px; accent-color: var(--series-1); }
  .rg-meta { font-size: 12px; color: var(--text-muted); font-variant-numeric: tabular-nums; }
  .rg-toggle { border: 1px solid var(--border); background: var(--surface-1); color: var(--text-secondary); border-radius: 7px; padding: 4px 9px; font-size: 12px; cursor: pointer; }
  .rg-body { display: none; padding: 0 12px 12px; }
  .region-group.open .rg-body { display: block; }
  .region-group .region-check-grid { grid-template-columns: repeat(4, 1fr); }
  @media (max-width: 720px) { .region-group .region-check-grid { grid-template-columns: repeat(2, 1fr); } }
  .region-group .region-check-item { background: var(--surface-1); font-size: 12.5px; }
  .opt-row { display: flex; align-items: flex-start; gap: 8px; margin-top: 14px; padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 12.5px; color: var(--text-secondary); line-height: 1.55; background: var(--page); cursor: pointer; }
  .opt-row input { margin-top: 3px; accent-color: var(--series-1); flex: none; }
  #bracketWrap { margin-top: 12px; }""")

# ---------- 0단계 HTML ----------
i0 = s.index('      <p class="hint">서울시 25개 구')
i1 = s.index('      <div class="grid" style="margin-top: 14px; display: none;">')
new0 = """      <p class="hint">전국 시·도별로 체크하면 해당 지역 매물 개수와 월세 총합(월간)이 합산됩니다. 「시·군·구 보기」를 누르면 시·군·구 단위로 고를 수 있습니다. 대상은 광고에 전입신고 불가를 적은 월세 매물(월세가 있는 보증부 월세 포함)이며 아파트는 제외했습니다. 판정 보류 매물은 넣지 않았습니다.</p>

      <label class="region-check-item region-select-all" id="regionSelectAllWrap">
        <input type="checkbox" id="regionSelectAll" />
        <span id="regionSelectAllText">전국 전체 선택</span>
      </label>
      <div id="regionGroups"></div>
      <p class="split-hint" id="regionSumHint">지역을 선택하면 매물 개수와 월세 총합이 자동으로 계산됩니다.</p>

"""
s = s[:i0] + new0 + s[i1:]

# ---------- 1단계: 1주택 비과세 옵션 ----------
rep("""          <input type="number" id="r4" min="0" max="100" step="0.1" value="10" />
        </label>
      </div>
    </section>""", """          <input type="number" id="r4" min="0" max="100" step="0.1" value="10" />
        </label>
      </div>
      <label class="opt-row"><input type="checkbox" id="excl1" checked /><span>1주택 소유자의 월세 소득은 비과세로 보고 과세 대상에서 뺍니다. 소득세법상 국내 1주택 소유자의 주택 임대소득은 원칙적으로 비과세입니다(기준시가 12억원 초과 주택 등은 예외인데, 이 도구는 주택 가격을 알 수 없어 반영하지 못합니다). 체크를 풀면 1주택 매물도 과세하는 최대 시나리오로 계산합니다.</span></label>
    </section>""")

# ---------- JS: 지역 블록 교체 ----------
a = s.index("  // ---- 0단계: 서울 25개 구별")
b = s.index("  // ---- formatting helpers ----")
newjs = """  // ---- 0단계: 전국 시·도 / 시·군·구별 전입 불가 월세 매물 수·월세 합계(만원, 월간) ----
  // 2026년 11월 수집, 4개 플랫폼, 중복 제거 후 아파트 제외 전입 불가 월세(월세>0) 매물. sim/make_region_data.py로 집계.
  var REGION_DATA = __REGION_DATA__;
  var SIDO_ORDER = ['서울','경기','인천','부산','대구','대전','광주·전남','울산','세종','강원','충북','충남','전북','경북','경남','제주','기타'];
  var SIDO_LABEL = { '기타': '기타(지역 미분류)' };
  var regionGroups = el('regionGroups');
  var allItems = [];
  var groups = [];
  SIDO_ORDER.forEach(function(sido){
    var data = REGION_DATA[sido]; if (!data) return;
    var names = Object.keys(data).sort(function(x, y){ return data[y][0] - data[x][0] || x.localeCompare(y, 'ko'); });
    var box = document.createElement('div'); box.className = 'region-group';
    var head = document.createElement('div'); head.className = 'rg-head';
    var lab = document.createElement('label');
    var gcb = document.createElement('input'); gcb.type = 'checkbox';
    var nm = document.createElement('span'); nm.textContent = SIDO_LABEL[sido] || sido;
    lab.appendChild(gcb); lab.appendChild(nm);
    var meta = document.createElement('span'); meta.className = 'rg-meta';
    var cnt = 0, val = 0; names.forEach(function(n){ cnt += data[n][0]; val += data[n][1]; });
    meta.textContent = '매물 ' + cnt.toLocaleString('ko-KR') + '개 · 월세 ' + val.toLocaleString('ko-KR') + '만원';
    var tg = document.createElement('button'); tg.type = 'button'; tg.className = 'rg-toggle'; tg.textContent = '시·군·구 보기 ▾';
    tg.addEventListener('click', function(){ var o = box.classList.toggle('open'); tg.textContent = o ? '시·군·구 접기 ▴' : '시·군·구 보기 ▾'; });
    head.appendChild(lab); head.appendChild(meta); head.appendChild(tg);
    var body = document.createElement('div'); body.className = 'rg-body';
    var grid = document.createElement('div'); grid.className = 'region-check-grid';
    var g = { cb: gcb, items: [], box: box };
    names.forEach(function(n){
      var l = document.createElement('label'); l.className = 'region-check-item';
      var c = document.createElement('input'); c.type = 'checkbox';
      var sp = document.createElement('span'); sp.textContent = n + ' ' + data[n][0].toLocaleString('ko-KR');
      l.title = n + ' · 매물 ' + data[n][0] + '개 · 월세 ' + data[n][1].toLocaleString('ko-KR') + '만원';
      l.appendChild(c); l.appendChild(sp); grid.appendChild(l);
      var it = { cb: c, count: data[n][0], value: data[n][1] };
      g.items.push(it); allItems.push(it);
      c.addEventListener('change', function(){ syncGroup(g); syncSelectAll(); updateRegionSum(); });
    });
    body.appendChild(grid); box.appendChild(head); box.appendChild(body); regionGroups.appendChild(box);
    gcb.addEventListener('change', function(){ g.items.forEach(function(it){ it.cb.checked = gcb.checked; }); gcb.indeterminate = false; syncSelectAll(); updateRegionSum(); });
    groups.push(g);
  });
  function syncGroup(g){
    var n = g.items.filter(function(it){ return it.cb.checked; }).length;
    g.cb.checked = n === g.items.length;
    g.cb.indeterminate = n > 0 && n < g.items.length;
  }
  var regionSelectAll = el('regionSelectAll');
  el('regionSelectAllText').textContent = '전국 전체 선택 (' + groups.length + '개 시·도, ' + allItems.length + '개 시·군·구)';
  regionSelectAll.addEventListener('change', function(){
    allItems.forEach(function(it){ it.cb.checked = regionSelectAll.checked; });
    groups.forEach(syncGroup);
    regionSelectAll.indeterminate = false;
    updateRegionSum();
  });
  function syncSelectAll(){
    var n = allItems.filter(function(it){ return it.cb.checked; }).length;
    regionSelectAll.checked = n === allItems.length;
    regionSelectAll.indeterminate = n > 0 && n < allItems.length;
  }

  function updateRegionSum(){
    var rentSum = 0, listingSum = 0, regionCount = 0;
    allItems.forEach(function(it){
      if (it.cb.checked){ rentSum += it.value; listingSum += it.count; regionCount++; }
    });
    el('regionSumHint').textContent = regionCount
      ? ('선택한 ' + regionCount + '개 시·군·구 · 매물 ' + listingSum.toLocaleString('ko-KR') + '개 · 월세 총합 ' + rentSum.toLocaleString('ko-KR') + '만원이 자동으로 계산되었습니다.')
      : '지역을 선택하면 매물 개수와 월세 총합이 자동으로 계산됩니다.';
    rentUnitEl.value = '10000';
    totalRentEl.value = rentSum;
    totalListingsEl.value = listingSum;
    recompute();
  }

""".replace("__REGION_DATA__", reg)
s = s[:a] + newjs + s[b:]

# ---------- 계산: 1주택 비과세 ----------
rep("""    var annualIncome = totalRentWon * 12; // @

    var estLandlords = N1 / 1 + N2 / 2 + N3 / 3 + N4 / 4;""",
"""    var annualAll = totalRentWon * 12; // 선택 지역 전체 월세의 연 환산
    var excl1 = el('excl1').checked;   // 1주택 소유자 월세는 비과세로 제외
    var taxableShare = excl1 ? (1 - r[0]) : 1; // 월세가 매물에 고르게 분포한다고 가정
    var annualIncome = annualAll * taxableShare; // @ (과세 대상 연간 임대수입)
    var exemptIncome = annualAll - annualIncome;

    var estLandlords = (excl1 ? 0 : N1 / 1) + N2 / 2 + N3 / 3 + N4 / 4;""")
rep("""      N: N, N1: N1, N2: N2, N3: N3, N4: N4,
      annualIncome: annualIncome,""", """      N: N, N1: N1, N2: N2, N3: N3, N4: N4,
      annualAll: annualAll, exemptIncome: exemptIncome, excl1: excl1,
      annualIncome: annualIncome,""")
rep("    el('statGrid').innerHTML =\n      statTile('연간 임대수입 (@)', fmtKorean(v.annualIncome), fmtWon(v.annualIncome)) +",
    "    el('statGrid').innerHTML =\n      statTile(v.excl1 ? '과세 대상 연간 임대수입 (@)' : '연간 임대수입 (@)', fmtKorean(v.annualIncome), v.excl1 ? ('1주택 비과세분 ' + fmtKorean(v.exemptIncome) + ' 제외') : fmtWon(v.annualIncome)) +")
rep("      ['① 연간 임대수입 (@ = 월세총합 × 12)', fmtWon(v.annualIncome)],",
    "      ['월세 총합 × 12 (선택 지역 전체 연간 월세)', fmtWon(v.annualAll)],\n      ['　└ 1주택 비과세분 (제외)', v.excl1 ? fmtWon(v.exemptIncome) : '제외 안 함'],\n      ['① 과세 대상 연간 임대수입 (@)', fmtWon(v.annualIncome)],")
rep("['② 추정 임대인 수 (N1/1+N2/2+N3/3+N4/4)', fmtNum(v.estLandlords, 2) + '명'],",
    "['② 추정 과세 대상 임대인 수 ' + (v.excl1 ? '(N2/2+N3/3+N4/4)' : '(N1/1+N2/2+N3/3+N4/4)'), fmtNum(v.estLandlords, 2) + '명'],")
rep("statTile('추정 임대인 수', fmtNum(v.estLandlords, 1) + '명') +", "statTile('추정 과세 대상 임대인 수', fmtNum(v.estLandlords, 1) + '명') +")
rep("    var taxBaseMax = Math.max(0, v.annualIncome - necessaryExpensesMax - basicDeductionMax);",
    "    var taxBaseMax = Math.max(0, v.annualAll - necessaryExpensesMax - basicDeductionMax);")
rep("    var necessaryExpensesMax = v.annualIncome * 0.5;", "    var necessaryExpensesMax = v.annualAll * 0.5;")
rep("      { label: '1주택', value: v.N1 / 1 },", "      { label: v.excl1 ? '1주택(비과세)' : '1주택', value: v.N1 / 1 },")
rep("    el('detailBody')", "    el('detailBody')")  # no-op sanity
# 비과세 체크 변경 시 재계산, 초기 전체 선택
rep("  // ---- other inputs ----", "  // ---- other inputs ----\n  el('excl1').addEventListener('change', recompute);")
rep("  // initial render\n  recompute();", "  // initial render: 전국 전체 선택으로 시작\n  regionSelectAll.checked = true;\n  regionSelectAll.dispatchEvent(new Event('change'));")

# ---------- 하단 한계 안내 ----------
rep("""      </div>
    </section>

  </div>
</div>""", """      </div>
    </section>

    <footer class="assump">
      <b>이 모델이 반영하지 못하는 것</b><br>
      · 1주택 소유자 비과세의 예외(기준시가 12억원 초과 등), 3주택 이상 보증금의 간주임대료, 등록 임대주택 세제 혜택은 반영하지 않습니다.<br>
      · 기본공제 400만원·200만원은 분리과세 제도의 공제인데, 이 모델은 종합과세 몫에도 같은 방식으로 적용합니다. 소득 구간별 누진공제도 구간마다 나눠 단순화했습니다.<br>
      · 주택 수, 등록 비율, 과세 방식, 소득 구간 비율의 기본값은 근거가 있는 통계가 아니라 예시이며, 값을 바꾸면 결과가 크게 달라집니다.<br>
      · 데이터는 2026년 11월 다방·직방·피터팬·당근마켓에 공개된 매물입니다. 같은 임대인이 올린 매물인지 알 수 없고, 오프라인으로만 맺은 계약은 포함되지 않습니다.
    </footer>

  </div>
</div>""")


# ---------- 길이 줄이기: 기본으로 접어 두기 ----------
# (a) 시·도 17줄 목록은 접어 두고, 전국 전체 선택 한 줄만 보이게
rep("""      <label class="region-check-item region-select-all" id="regionSelectAllWrap">
        <input type="checkbox" id="regionSelectAll" />
        <span id="regionSelectAllText">전국 전체 선택</span>
      </label>""", """      <div class="region-top">
        <label class="region-check-item region-select-all" id="regionSelectAllWrap">
          <input type="checkbox" id="regionSelectAll" />
          <span id="regionSelectAllText">전국 전체 선택</span>
        </label>
        <button type="button" class="rg-toggle" id="regionOpen">시·도별로 고르기 ▾</button>
      </div>""")
rep("  function syncGroup(g){", """  el('regionOpen').addEventListener('click', function(){
    var o = regionGroups.classList.toggle('open');
    this.textContent = o ? '시·도 목록 접기 ▴' : '시·도별로 고르기 ▾';
  });
  function syncGroup(g){""")
# (b) 소득 구간 8개 입력은 접기
rep("""        <div class="grid cols-4" id="bracketGrid" style="margin-top: 14px;"></div>
      </div>""", """        <div class="grid cols-4" id="bracketGrid" style="margin-top: 14px;"></div>
        </details>
      </div>""")
rep("""      <div id="bracketWrap">
        <p class="hint" style="margin-top: 18px;">종합과세 비율 중 소득 구간별 분포입니다. 막대의 경계선을 드래그하면 8개 구간 비율이 조정됩니다 (종합과세 비율 안에서 합계 항상 100%).</p>""",
"""      <div id="bracketWrap">
        <details class="fold" style="margin-top: 16px;">
        <summary>종합과세 소득 구간별 비율 설정 (8개 구간, 필요하면 열어서 조정)</summary>
        <p class="hint" style="margin-top: 12px;">종합과세 비율 중 소득 구간별 분포입니다. 막대의 경계선을 드래그하면 8개 구간 비율이 조정됩니다 (종합과세 비율 안에서 합계 항상 100%).</p>""")
# (c) 계산 과정 표·그래프는 접기 (핵심 지표·게이지·환산은 그대로 보임)
rep("""      <div class="table-scroll">
        <table class="detail" id="detailTable">""", """      <details class="fold" id="calcDetails" style="margin-top: 18px;">
      <summary>계산 과정과 그래프 자세히 보기</summary>
      <div class="table-scroll">
        <table class="detail" id="detailTable">""")
rep("""      <div class="impact-section" id="impactBlock">""", """      </details>

      <div class="impact-section" id="impactBlock">""")
# (d) 안내 문구 줄이기
rep("""임대인마다 과세 방식이 다를 수 있으므로, 1주택~4주택 비율처럼 분리과세/종합과세 비율과 종합과세 안의 소득 구간별 비율을 입력합니다. 경계선을 드래그하거나 숫자를 입력하세요 (모두 과세표준 기준, 합계는 항상 100%).""",
    """분리과세와 종합과세 비율을 정합니다. 경계선을 드래그하거나 숫자를 입력하세요(합계는 항상 100%).""")
rep("""전체 매물 중 몇 %가 몇 주택자의 매물인지 입력하세요. 추정 임대인 수 = N1/1 + N2/2 + N3/3 + N4/4. 경계선을 드래그하거나 숫자를 입력하면 비율이 바뀌고, 합계는 항상 100%로 유지됩니다.""",
    """전체 매물 중 몇 %가 몇 주택 소유자의 매물인지 정합니다. 경계선을 드래그하거나 숫자를 입력하세요(합계는 항상 100%).""")
rep("""등록/미등록 임대사업자 비율에 따라 필요경비율(등록 60%, 미등록 50%)과 기본공제액(등록 400만원, 미등록 200만원)이 다르게 적용됩니다. 경계선을 드래그하거나 숫자를 입력하세요.""",
    """등록 여부에 따라 필요경비율(등록 60%, 미등록 50%)과 기본공제(등록 400만원, 미등록 200만원)가 달라집니다.""")
rep("""전국 시·도별로 체크하면 해당 지역 매물 개수와 월세 총합(월간)이 합산됩니다. 「시·군·구 보기」를 누르면 시·군·구 단위로 고를 수 있습니다. 대상은 광고에 전입신고 불가를 적은 월세 매물(월세가 있는 보증부 월세 포함)이며 아파트는 제외했습니다. 판정 보류 매물은 넣지 않았습니다.""",
    """처음에는 전국 전체로 계산합니다. 지역을 좁히려면 「시·도별로 고르기」를 누르세요. 대상은 광고에 전입신고 불가를 적은 월세 매물이며 아파트와 판정 보류 매물은 뺐습니다.""")

# ---------- 기사 컨셉 테마 ----------
theme = (ROOT / "sim" / "theme_patch.txt").read_text(encoding="utf-8")
rep("</style>\n</head>", theme + "</style>\n</head>")
rep("<style>\n  :root {", '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css">\n<style>\n  :root {')
rep('    <header class="top">\n      <div>\n        <h1>', '    <a class="back" href="./">← 전입신고 불가 매물 추적기로 돌아가기</a>\n    <header class="top">\n      <div>\n        <div class="chip">SIMULATOR</div>\n        <h1>')

# ---------- 컴팩트 레이아웃: 입력(왼쪽) + 결과(오른쪽, 따라다님) ----------
rep("    <!-- STEP 0: 기초 데이터 -->", '    <div class="layout"><div class="inputs">\n    <!-- STEP 0: 기초 데이터 -->')
rep("    <!-- RESULTS -->\n    <section class=\"card\">", '    </div>\n    <aside class="resultcol">\n    <!-- RESULTS -->\n    <section class="card">')
rep("    </section>\n\n    <footer class=\"assump\">", "    </section>\n    </aside></div>\n\n    <footer class=\"assump\">")

# 맨 위 경고문을 짧게
d0 = s.index('<div class="disclaimer">')
d1 = s.index("</div>", d0) + len("</div>")
s = s[:d0] + ('<div class="disclaimer"><b>세금 계산기가 아닙니다.</b> 임대인 정보가 없는 매물 데이터에 가정값을 넣어 보는 시뮬레이션이며, '
              '기본 가정값은 근거가 확인된 통계가 아닌 예시입니다. 이 모델의 한계는 맨 아래에 있습니다.</div>') + s[d1:]

# 0단계 안내 문구를 한 줄로
rep("처음에는 전국 전체로 계산합니다. 지역을 좁히려면 「시·도별로 고르기」를 누르세요. 대상은 광고에 전입신고 불가를 적은 월세 매물이며 아파트와 판정 보류 매물은 뺐습니다.",
    "전입 불가 월세 매물(아파트·보류 제외)입니다. 기본은 전국 전체이며, 좁히려면 「시·도별로 고르기」를 누르세요.")

# 하단 한계 안내는 접어 두기
rep('<footer class="assump">\n      <b>이 모델이 반영하지 못하는 것</b><br>',
    '<footer class="assump"><details class="fold"><summary>이 모델이 반영하지 못하는 것</summary><div style="padding-top:2px">')
rep("    </footer>", "    </div></details></footer>")

# 좁은 화면용 하단 고정 요약 막대
rep('<div id="tooltip"></div>', '<div id="tooltip"></div>\n<div class="minibar" id="miniBar"><span>최종 잠재세수</span><b id="miniVal">-</b></div>')
rep("  function render(v){", "  function render(v){\n    var mv = el('miniVal'); if (mv) mv.textContent = fmtKorean(v.finalTax);")

# ---------- 줄글 최소화 ----------
import re
# 각 단계의 안내 문단(.hint) 전부 삭제
s = re.sub(r'[ \t]*<p class="hint"[^>]*>.*?</p>\n?', "", s, flags=re.S)
# 부제를 한 줄로
rep('<p class="sub">2026년 11월 다방·직방·피터팬·당근마켓에서 모은 전국 매물 가운데, 광고에 전입신고 불가를 밝힌 <b>월세 매물 8,924건</b>(아파트 제외)의 임대소득이 정상적으로 신고·과세될 경우 발생할 수 있는 <b>잠재 세수 규모</b>를 추정합니다.</p>',
    '<p class="sub">전입신고 불가를 밝힌 전국 <b>월세 매물 8,924건</b>(아파트 제외)의 임대소득이 과세된다면?</p>')
# 경고문을 한 줄로
d0 = s.index('<div class="disclaimer">')
d1 = s.index("</div>", d0) + len("</div>")
s = s[:d0] + '<div class="disclaimer"><b>세금 계산기가 아닌 시뮬레이션입니다.</b> 가정값은 예시이며, 한계는 맨 아래에 있습니다.</div>' + s[d1:]
# 1주택 비과세 옵션: 한 줄 라벨 + 자세한 설명은 마우스를 올렸을 때만
o0 = s.index('<label class="opt-row">')
o1 = s.index("</label>", o0) + len("</label>")
s = s[:o0] + ('<label class="opt-row" title="소득세법상 국내 1주택 소유자의 주택 임대소득은 원칙적으로 비과세입니다(기준시가 12억원 초과 주택 등은 예외이며 이 도구는 반영하지 못합니다). 체크를 풀면 1주택 매물도 과세하는 최대 시나리오로 계산합니다.">'
              '<input type="checkbox" id="excl1" checked /><span>1주택 소유자 월세는 비과세로 제외</span></label>') + s[o1:]
# 지역 합계 문구를 짧게
rep("'선택한 ' + regionCount + '개 시·군·구 · 매물 ' + listingSum.toLocaleString('ko-KR') + '개 · 월세 총합 ' + rentSum.toLocaleString('ko-KR') + '만원이 자동으로 계산되었습니다.'",
    "regionCount + '개 시·군·구 · 매물 ' + listingSum.toLocaleString('ko-KR') + '개 · 월세 합계(월) ' + rentSum.toLocaleString('ko-KR') + '만원'")
rep("'지역을 선택하면 매물 개수와 월세 총합이 자동으로 계산됩니다.'", "'지역을 선택하세요'")
# 계산 중 안내 배너 숨김
s = s.replace("</style>\n</head>", ".note-banner{display:none!important}\n.opt-row{cursor:help}\n</style>\n</head>", 1)

# ---------- 기사에 박스로 넣을 때(?embed=1): 머리말 숨기고 높이를 부모 창에 알림 ----------
embed_js = """<script>
(function(){
  if(!/[?&]embed=1/.test(location.search)) return;
  document.documentElement.classList.add('embed');
  var last = 0;
  function send(){
    var w = document.querySelector('.wrap'); if(!w) return;
    var h = Math.ceil(w.getBoundingClientRect().height);
    if(h === last) return; last = h;
    try{ parent.postMessage({type:'sim-h', h:h}, '*'); }catch(e){}
  }
  if(window.ResizeObserver) new ResizeObserver(send).observe(document.querySelector('.wrap'));
  window.addEventListener('load', send); window.addEventListener('resize', send);
  setTimeout(send, 300); setTimeout(send, 1200);
})();
</script>
"""
rep("</body>", embed_js + "</body>")

# ---------- 기본값: 임대인 구조 25/25/25/25, 사업자 50/50, 과세방식 50/50 ----------
for rid, old, new in (('r1','40','25'),('r2','30','25'),('r3','20','25'),('r4','10','25'),
                      ('regRatioNum','30','50'),('unregRatioNum','70','50'),('sepRatio','60','50'),('compRatio','40','50')):
    rep('id="%s" min="0" max="100" step="0.1" value="%s" />' % (rid, old), 'id="%s" min="0" max="100" step="0.1" value="%s" />' % (rid, new))
rep("values: [40, 30, 20, 10],", "values: [25, 25, 25, 25],")
rep("values: [30, 70],", "values: [50, 50],")
rep("values: [60, 40],", "values: [50, 50],")

# ---------- 게이지 라벨: 마우스를 올렸을 때만 표시 ----------
rep('<div class="gauge-marker" id="gaugeMarker">', '<div class="gauge-marker" id="gaugeMarker" tabindex="0">')
rep("</style>\n</head>", """.gauge-marker{cursor:pointer;outline:none}
.gauge-marker::after{content:"";position:absolute;left:-14px;right:-14px;top:-14px;bottom:-14px}
.gauge-marker-label{opacity:0;visibility:hidden;transition:opacity .15s;pointer-events:none}
.gauge-marker:hover .gauge-marker-label,.gauge-marker:focus .gauge-marker-label{opacity:1;visibility:visible}
</style>
</head>""")

(ROOT / "simulator.html").write_text(s, encoding="utf-8", newline="")
print("written", len(s))
