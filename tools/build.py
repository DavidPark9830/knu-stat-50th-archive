from pathlib import Path
import json,html,re,collections,urllib.parse,sys
ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)>1:ROOT=Path(sys.argv[1])
def load(name):return json.loads((ROOT/'data'/name).read_text())
PHOTOS=load('photos.json');SECTIONS=load('records.json');CHAPTERS=load('chapters.json');DOCS=load('yearbooks.json');LABS=load('labs.json');BY_ID={p['id']:p for p in PHOTOS}
def esc(s):return html.escape(str(s),quote=True)
def url(path):return urllib.parse.quote(path,safe='/#?=&:%')
def original(p):return 'https://raw.githubusercontent.com/DavidPark9830/knu-stat-50th-archive/main/'+url(p['original_path'])
def datekey(s):
 match=re.search(r'(?:19|20)\d{2}(?:[-.]\d{1,2})?(?:[-.]\d{1,2})?',s)
 if not match:return '9999-99-99'
 nums=re.findall(r'\d+',match.group());return '-'.join([nums[0]]+[n.zfill(2) for n in nums[1:]])
def photo(p,primary=False):
 date=p.get('date') or '날짜 미상';tags=p.get('tags',[]);dimensions=f'{p["width"]:,} × {p["height"]:,} px';desc=p.get('description','');classes='photo-card primary-photo filterable' if primary else 'photo-card';id=f'photo-{p["id"]}' if primary else ''
 search=' '.join([p['title'],date,p.get('date_basis',''),' '.join(tags),p.get('group',''),desc]);source=p.get('source','');source_a=f'<a class="photo-source" href="{esc(url(source))}" target="_blank" rel="noopener">출처</a>' if source else ''
 return f'''<figure class="{classes}" {'id="'+esc(id)+'"' if id else ''} data-search="{esc(search)}" data-tags="{esc('|'.join(tags))}" data-status="{esc(p.get('status',''))}"><button type="button" class="photo-open" data-photo="{esc(p['id'])}" aria-label="{esc(p['title'])} 확대"><img src="{esc(url(p['preview_path']))}" alt="{esc(p['title'])}" width="{p['width']}" height="{p['height']}" loading="lazy" decoding="async"></button><figcaption><h3>{esc(p['title'])}</h3><div class="photo-date">{esc(date)}{(' · '+esc(p['date_basis'])) if p.get('date_basis') else ''}</div><div class="tags">{''.join('<span class="tag">'+esc(t)+'</span>' for t in tags)}</div><p class="photo-quality">{esc(dimensions)} · {esc(p.get('status',''))}</p>{'<p class="photo-desc">'+esc(desc)+'</p>' if desc else ''}<div class="photo-links"><a href="{esc(original(p))}" data-original-path="{esc(url(p['original_path']))}" target="_blank" rel="noopener">원본 보관본</a>{source_a}</div></figcaption></figure>'''
def table(rows):
 if not rows:return ''
 header=rows[0];body=rows[1:]
 return '<div class="table-scroll"><table><thead><tr>'+''.join('<th scope="col">'+esc(c)+'</th>' for c in header)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>' for row in body)+'</tbody></table></div>'
def source_link(s):
 path=s['url']; attr=''
 if path.startswith('photos/'):
  attr=' data-original-path="'+esc(url(path))+'"'
  path='https://raw.githubusercontent.com/DavidPark9830/knu-stat-50th-archive/main/'+url(path)
 return '<a href="'+esc(url(path))+'"'+attr+' target="_blank" rel="noopener">'+esc(s['label'])+'</a>'
def record(r):
 photos=[BY_ID[x] for x in r['photo_ids'] if x in BY_ID];tags=sorted(set(t for p in photos for t in p.get('tags',[])));statuses=sorted(set(p.get('status','') for p in photos));search=' '.join([r['title'],r['date'],' '.join(r['paragraphs']),' '.join(r['facts']),' '.join(tags),' '.join(p['title'] for p in photos)])
 paragraphs=''.join('<p>'+esc(p)+'</p>' for p in r['paragraphs']);facts='<div class="facts">'+''.join('<span>'+esc(f)+'</span>' for f in r['facts'])+'</div>' if r['facts'] else ''
 pictures='<div class="gallery">'+''.join(photo(p) for p in photos)+'</div>' if photos else ''
 stills=''.join('<figure class="video-still"><img src="'+esc(url(p))+'" alt="'+esc(r['title'])+' 미리보기" loading="lazy" decoding="async"></figure>' for p in r['previews'])
 sources='<div class="sources">'+''.join(source_link(s) for s in r['sources'])+'</div>'
 refs=''
 if r.get('local_references'):
  labels=list(dict.fromkeys(s['label'] for s in r['local_references'] if s['label']))
  if labels:refs='<p class="local-note">로컬 원본 보관: '+esc(' · '.join(labels))+'. 대용량 행사 영상 원본은 공개 웹문서에 업로드하지 않았습니다.</p>'
 return f'<article class="record filterable" id="{esc(r["id"])}" data-search="{esc(search)}" data-tags="{esc("|".join(tags))}" data-status="{esc("|".join(statuses))}"><div class="date">{esc(r["date"])}<span class="basis">{esc(r["date_basis"])}</span></div><h3>{esc(r["title"])}</h3>{paragraphs}{facts}{pictures}{stills}{"".join(table(t) for t in r["tables"])}{refs}{sources}</article>'
counts=collections.Counter(p['chapter'] for p in PHOTOS);total=sum(len(s['records']) for s in SECTIONS);tags=collections.Counter(t for p in PHOTOS for t in p['tags']);status=collections.Counter(p.get('status','') for p in PHOTOS)
parts=['''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="경북대학교 통계학과 50주년을 위한 연혁·수상·학술교류·동문·기념행사 사진 자료 아카이브."><title>경북대학교 통계학과 50주년 자료 아카이브</title><link rel="stylesheet" href="web/style.css"><script src="web/app.js" defer></script></head><body><a class="skip-link" href="#main">본문으로 건너뛰기</a><aside><a class="brand" href="#main">경북대학교 통계학과<br>50주년 자료 아카이브</a><p class="aside-caption">기록과 사진으로 살펴보는 학과의 시간</p><nav aria-label="자료 목차">''']
for c in CHAPTERS:parts.append(f'<a href="#chapter-{c["number"]:02}"><span>{c["number"]:02}</span>{esc(c["title"])}</a>')
parts.append('''<div class="nav-divider"><a href="#research-records">세부 조사 기록</a><a href="#yearbooks">졸업앨범 원문</a><a href="#research-labs">교수·연구실 자료</a><a href="#documents">사업·학회 문서</a><a href="https://github.com/DavidPark9830/knu-stat-50th-archive" target="_blank" rel="noopener">GitHub 저장소</a></div></nav></aside><main id="main"><header><p class="eyebrow">KNU Statistics · 50th Anniversary Archive</p><h1>경북대학교 통계학과<br>50주년 자료 아카이브</h1>''')
parts.append(f'<div class="meta">2026년 10월 21일 정리 · 사진 {len(PHOTOS):,}장 · 조사 기록 {total:,}건 · 졸업앨범 원문 {len(DOCS)}건</div>')
parts.append('''<p>학과 연혁, 학술·교육 성과, 학생 수상, 동문과 장학, 국제교류의 조사 자료를 모았습니다. 큰 챕터별 사진과 날짜순 기록을 함께 확인할 수 있습니다.</p><p>사진은 문서 안에서 바로 표시되며 클릭하면 원본 보관본을 엽니다. 날짜가 일부만 확인된 자료는 해당 연도·월까지만 표기하고, 날짜 미상 자료는 뒤에 배치했습니다.</p><p class="contents-note">졸업앨범 연도는 동창회 홈페이지 분류를 우선했습니다. 같은 사진의 스캔본을 중복 등록하지 않았으며, 동창회 보관본과 스캔에서만 확인되는 추가 사진을 구분했습니다.</p></header><noscript><p class="contents-note">사진과 조사 내용은 자바스크립트 없이도 볼 수 있습니다. 검색·필터·확대 보기는 자바스크립트가 필요합니다.</p></noscript><form class="filters" role="search" onsubmit="return false"><label>검색<input id="search" type="search" placeholder="연도, 행사, 인물, 수상명" autocomplete="off"></label><label>사진 태그<select id="tag"><option value="">전체 태그</option>''')
parts.extend('<option value="'+esc(t)+'">'+esc(t)+f' ({n})</option>' for t,n in tags.most_common())
parts.append('</select></label><label>자료 상태<select id="status"><option value="">전체 상태</option>')
parts.extend('<option value="'+esc(t)+'">'+esc(t)+f' ({n})</option>' for t,n in status.most_common() if t)
parts.append(f'</select></label><button id="reset" type="button">초기화</button><output id="filter-result" aria-live="polite">사진 {len(PHOTOS):,}장 · 조사 기록 {total:,}건 표시</output></form>')
for c in CHAPTERS:
 number=c['number'];ps=sorted([p for p in PHOTOS if p['chapter']==number],key=lambda p:(datekey(p.get('date','')),p['title'],p['id']));groups=collections.OrderedDict()
 for p in ps:
  m=re.search(r'(?:19|20)\d{2}',p.get('date',''));year=m.group()+'년' if m else '날짜 미상';groups.setdefault(year,[]).append(p)
 parts.append(f'<section class="chapter" id="chapter-{number:02}"><h2><span class="number">{number:02}</span>{esc(c["title"])}<small class="visible-count">{len(ps)}장</small></h2>')
 for year,items in groups.items():parts.append('<div class="year-group"><h3 class="year">'+esc(year)+'</h3><div class="gallery">'+''.join(photo(p,True) for p in items)+'</div></div>')
 parts.append('<p class="empty-result" hidden>선택한 조건에 맞는 사진이 없습니다.</p></section>')
parts.append('<div class="research-head" id="research-records"><h2>세부 조사 기록<small>분류별 날짜순</small></h2></div><div class="research-index">'+''.join('<a href="#records-'+s['id']+'">'+esc(s['title'])+'</a>' for s in SECTIONS)+'</div>')
for sec in SECTIONS:
 parts.append('<section class="record-section" id="records-'+esc(sec['id'])+'"><h2>'+esc(sec['title'])+f'<small>{len(sec["records"])}건</small></h2>')
 parts.extend(record(r) for r in sorted(sec['records'],key=lambda r:(datekey(r['date']),r['title'])))
 parts.append('</section>')
parts.append('<section class="document-section" id="yearbooks"><h2>졸업앨범 원문<small>동창회 분류 연도 우선</small></h2><p class="section-desc">동일 사진은 위 갤러리에서 대표본으로 확인할 수 있습니다. 아래는 지면과 연도 표기를 대조하기 위한 PDF 원문입니다.</p><div class="document-grid">')
for d in sorted(DOCS,key=lambda x:(x['year'],x['title'])):parts.append('<article class="document" id="'+esc(d['id'])+'"><h3>'+esc(d['title'])+'</h3><iframe src="'+esc(url(d['path']))+'#page=1&amp;view=FitH" title="'+esc(d['title'])+' PDF 미리보기" loading="lazy"></iframe><p>'+esc(d['description'])+'</p><a href="'+esc(url(d['path']))+'" target="_blank" rel="noopener">PDF 원문 · '+str(d['pages'])+'쪽</a></article>')
parts.append('</div></section><section class="lab-section" id="research-labs"><h2>교수·연구실별 공개 자료</h2>')
parts.extend(table(t) for t in LABS['tables']);parts.append('<div class="sources">'+''.join('<a href="'+esc(s['url'])+'" target="_blank" rel="noopener">'+esc(s['label'])+'</a>' for s in LABS['sources'])+'</div></section>')
parts.append('<section class="document-section" id="documents"><h2>사업·학회 원문 문서</h2><div class="document-grid">')
yearbook_paths={d['path'] for d in DOCS}
document_titles={d['path']:d['title'] for d in load('documents.json')}
for f in sorted((ROOT/'docs').iterdir()):
 rel=str(f.relative_to(ROOT))
 if rel in yearbook_paths:continue
 title=document_titles.get(rel,f.stem);parts.append('<article class="document"><h3>'+esc(title)+'</h3>')
 if f.suffix.lower()=='.pdf':parts.append('<iframe src="'+esc(url(rel))+'#page=1&amp;view=FitH" title="'+esc(title)+' PDF 미리보기" loading="lazy"></iframe>')
 parts.append('<a href="'+esc(url(rel))+'" target="_blank" rel="noopener">'+esc(f.suffix[1:].upper())+' 문서 열기</a></article>')
parts.append('''</div></section><footer>경북대학교 통계학과 50주년 기념을 위해 정리한 조사 자료 아카이브입니다.<br>각 자료의 날짜·인물·수상 구분은 설명과 원문 출처를 함께 확인해 주세요. 사진과 문서의 권리는 각 원저작자에게 있습니다.<br>기념영상 대본, 더빙 비교, 계정 정보와 작업용 원본 코드는 공개 자료에 포함하지 않았습니다.</footer></main><dialog id="photo-dialog" aria-labelledby="dialog-title"><div class="dialog-head"><h2 id="dialog-title">사진 확대</h2><button type="button" class="dialog-close" id="dialog-close">닫기</button></div><div class="dialog-image"><img id="dialog-image" alt=""></div><p class="dialog-caption" id="dialog-caption"></p><div class="dialog-links"><a id="dialog-original" target="_blank" rel="noopener">원본 보관본 열기</a><a id="dialog-source" target="_blank" rel="noopener">출처 열기</a></div></dialog></body></html>''')
(ROOT/'index.html').write_text('\n'.join(parts));print('Rendered',ROOT/'index.html',len(PHOTOS),'photos',total,'records')
