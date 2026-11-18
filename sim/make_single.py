# -*- coding: utf-8 -*-
"""제출용 단일 파일 만들기: index.html + 종이 배경 + 리플릿 이미지 2장 + 계산기(simulator.html)를 파일 하나로 합친다.
사용: python sim/make_single.py [출력경로]
기본 출력: 바탕 화면의 제출용_index.html
원본(index.html 등)은 건드리지 않는다. 수정은 원본에서 하고, 제출 직전에 이 스크립트를 다시 돌린다."""
import base64, io, pathlib, re, sys
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.home() / "OneDrive" / "바탕 화면" / "제출용_index.html"

html = (ROOT / "index.html").read_text(encoding="utf-8")
sim = (ROOT / "simulator.html").read_text(encoding="utf-8")


def rep(text, a, b, count=1):
    assert text.count(a) == count, (text.count(a), a[:70])
    return text.replace(a, b)


def b64(data, mime):
    return "data:%s;base64,%s" % (mime, base64.b64encode(data).decode("ascii"))


# 1) 종이 배경
paper = b64((ROOT / "paper.jpg").read_bytes(), "image/jpeg")
html = rep(html, "url(paper.jpg)", "url(%s)" % paper)

# 2) 리플릿 이미지: 줄여서 data URI로, 눌렀을 때 새 탭 원본 보기는 blob으로
for i in (1, 2):
    im = Image.open(ROOT / "img" / ("leaflet_%d.jpg" % i)).convert("RGB")
    w = 2400
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=72, optimize=True, progressive=True)
    uri = b64(buf.getvalue(), "image/jpeg")
    html = rep(html, '<a href="img/leaflet_%d.jpg" target="_blank" rel="noopener"><img data-src="img/leaflet_%d.jpg"' % (i, i),
               '<a href="#"><img data-src="%s"' % uri)

# 3) 계산기: 소스를 문서 안에 넣고, 실행 때 blob 주소로 iframe에 연결
sim2 = sim
sim2 = re.sub(r'\s*<a class="back" href="\./">.*?</a>', "", sim2, count=1, flags=re.S)           # 돌아가기 링크 제거
sim2 = rep(sim2, "if(!/[?&]embed=1/.test(location.search)) return;",
           "if(!(/[?&]embed=1/.test(location.search) || window.parent !== window)) return;")             # blob에서는 부모 유무로 판단
sim2 = sim2.replace("</script>", "<\\/script>")
sim2 = sim2.replace("<!--", "<\\!--")   # HTML 주석 시작 표시가 script 안에서 특수 상태를 만들지 않게
html = rep(html, '<iframe id="simframe" src="simulator.html?embed=1" title="전입신고 불가 월세 매물 잠재세수 계산기" loading="lazy"></iframe>',
           '<iframe id="simframe" title="전입신고 불가 월세 매물 잠재세수 계산기"></iframe>')
html = rep(html, '<a href="simulator.html" target="_blank" rel="noopener">새 창에서 크게 보기</a>',
           '<a href="#" id="simopen">새 창에서 크게 보기</a>')

loader = '''<script type="text/plain" id="simsrc">%s</script>
<script>
(function(){
  var srcEl=document.getElementById('simsrc'); if(!srcEl) return;
  var text=srcEl.textContent.replace(/<\\\\\\/script/g,'</script').replace(/<\\\\!--/g,'<!--'), url=null;
  function blobUrl(){ if(!url) url=URL.createObjectURL(new Blob([text],{type:'text/html'})); return url; }
  var f=document.getElementById('simframe');
  if(f){
    var load=function(){ if(!f.getAttribute('src')) f.setAttribute('src',blobUrl()); };
    if('IntersectionObserver' in window){ var io=new IntersectionObserver(function(es){ if(es.some(function(e){return e.isIntersecting;})){ load(); io.disconnect(); } },{rootMargin:'800px'}); io.observe(f); } else { load(); }
  }
  var op=document.getElementById('simopen'); if(op) op.addEventListener('click',function(e){ e.preventDefault(); window.open(blobUrl(),'_blank'); });
  document.querySelectorAll('#leafModal a').forEach(function(a){ a.addEventListener('click',function(e){
    e.preventDefault(); var im=a.querySelector('img'); if(!im||!im.src) return;
    fetch(im.src).then(function(r){return r.blob();}).then(function(b){ window.open(URL.createObjectURL(b),'_blank'); });
  }); });
})();
</script>
''' % sim2
html = rep(html, "</body></html>", loader + "</body></html>")

# 4) 남은 로컬 파일 참조 점검
refs = set(re.findall(r'(?:src|href)="([^"#]+)"', html)) | set(re.findall(r"url\(['\"]?([^)'\"]+)['\"]?\)", html))
local = [r for r in refs if not re.match(r"(https?:|data:|mailto:|//|blob:)", r)]
print("남은 로컬 참조:", local)

OUT.write_text(html, encoding="utf-8", newline="")
print("저장:", OUT, "크기 %.2f MB" % (OUT.stat().st_size / 1e6))
