// 제출용 단일 파일 정적 점검: 스크립트 문법, 계산기 소스 복원, 태그 짝, 이미지 개수
const fs = require('fs');
const h = fs.readFileSync(process.argv[2], 'utf8');

// 계산기 소스를 담은 text/plain 블록은 따로 떼어 낸다
const start = h.indexOf('<script type="text/plain" id="simsrc">');
const end = h.indexOf('</script>', start) + '</script>'.length;
const raw = h.slice(start + '<script type="text/plain" id="simsrc">'.length, end - '</script>'.length);
const hh = h.slice(0, start) + h.slice(end);

const scripts = [...hh.matchAll(/<script(?![^>]*application\/json)[^>]*>([\s\S]*?)<\/script>/g)].map(x => x[1]);
let ok = 0;
scripts.forEach((c, i) => { try { new Function(c); ok++; } catch (e) { console.log('SCRIPT ERR', i, e.message); } });
console.log('스크립트', scripts.length, '개 중 문법 정상', ok);

console.log('원문에 남은 닫는 script(text/plain 안, 0이어야 정상):', (raw.match(/<\/script>/g) || []).length, '| 주석 시작(0이어야 정상):', (raw.match(/<!--/g) || []).length);
const sim = raw.split('<\\/script').join('</script').split('<\\!--').join('<!--');
console.log('계산기 소스 복원 길이', sim.length, '| 여는 script', (sim.match(/<script/g) || []).length, '| 닫는 script', (sim.match(/<\/script>/g) || []).length);
[...sim.matchAll(/<script>([\s\S]*?)<\/script>/g)].forEach(x => {
  try { new Function(x[1]); console.log('계산기 스크립트 문법 정상'); } catch (e) { console.log('계산기 SCRIPT ERR', e.message); }
});
console.log('div 짝', (h.match(/<div/g) || []).length, (h.match(/<\/div>/g) || []).length);
console.log('data URI 이미지', (h.match(/data:image\/jpeg;base64/g) || []).length);
console.log('남은 simulator.html 참조', (h.match(/simulator\.html/g) || []).length, '| img/ 참조', (h.match(/img\/leaflet/g) || []).length, '| paper.jpg 참조', (h.match(/paper\.jpg/g) || []).length);
