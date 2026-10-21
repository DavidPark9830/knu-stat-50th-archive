"""자료목록·사진 해시·문서의 내부 링크를 검증합니다. 표준 파이썬만 필요합니다."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,hashlib,sys,collections,os,unicodedata
ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)>1:ROOT=Path(sys.argv[1])
class Document(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.photos=0;self.records=0;self.images=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  for k in ['src','href']:
   if a.get(k):self.links.append(a[k])
  c=a.get('class','').split()
  self.photos+='primary-photo' in c;self.records+='record' in c
  self.images+=tag=='img' and bool(a.get('src'))
d=Document();d.feed((ROOT/'index.html').read_text());counts=collections.Counter(d.ids)
assert not [k for k,n in counts.items() if n>1],'重複ID'
errors=[]
for u in d.links:
 p=urlsplit(u)
 if p.scheme or p.netloc:continue
 if p.path and not (ROOT/unquote(p.path)).is_file():errors.append('없는 파일: '+u)
 if not p.path and p.fragment and p.fragment not in counts:errors.append('없는 문서 위치: '+u)
assert not errors,'\n'.join(errors)
photos=json.loads((ROOT/'data/photos.json').read_text());records=json.loads((ROOT/'data/records.json').read_text())
assert d.photos==len(photos)==1027;assert d.records==sum(len(s['records']) for s in records)==497
assert len({p['original_path'] for p in photos})==len(photos)
for p in photos:
 assert (ROOT/p['preview_path']).is_file(),p['id']
 assert hashlib.sha256((ROOT/p['original_path']).read_bytes()).hexdigest()==p['sha256'],p['id']
for folder in ['data','web']:
 for f in (ROOT/folder).rglob('*'):
  if f.is_file():
   t=f.read_text()
   for forbidden in ['/Volumes/','/Users/','세상은 지금','대본/','더빙비교/','access_token','Bearer ']:assert forbidden not in t,(str(f),forbidden)

# 확장자 앞의 점 외에는 파일명에 점·문장부호를 사용하지 않습니다.
for base,dirs,names in os.walk(ROOT):
 dirs[:]=[d for d in dirs if not d.startswith('.')]
 for folder in dirs:assert folder.isascii() and len(folder)<=20,('폴더명',str(Path(base)/folder))
 for name in names:
  if name.startswith('.'):continue
  stem=unicodedata.normalize('NFC',Path(name).stem)
  assert name.isascii() and len(name)<=24 and all(c.isalnum() or c in '_-' for c in stem),('파일명 기호',str(Path(base)/name))

print(f'검사 완료: 사진 {d.photos:,}장, 조사 기록 {d.records:,}건, 모든 사진 SHA-256 일치, 내부 링크 정상')
