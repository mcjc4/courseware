#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
courseware-site 导航首页+管理页生成器 v2
变更：筛选改为弹窗+勾选+搜索模式；新增 manage.html 标签管理页
"""
import os, re, glob, html, json
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
LESSONS_DIR = os.path.join(ROOT, 'lessons')
OUT = os.path.join(ROOT, 'index.html')
MANAGE_OUT = os.path.join(ROOT, 'manage.html')


def extract_meta(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            head = f.read(200000)
    except Exception:
        return {'title': '未命名课件', 'sub': '', 'subject': '', 'chapter': '',
                'knowledge': '', 'source': '', 'type': '', 'tags': '', 'number': ''}
    info = {'title': '未命名课件', 'sub': '', 'subject': '', 'chapter': '',
            'knowledge': '', 'source': '', 'type': '', 'tags': '', 'number': '',
            'method': '', 'date': ''}
    m = re.search(r'<title[^>]*>(.*?)</title>', head, re.S | re.I)
    if m:
        t = html.unescape(re.sub(r'\s+', ' ', m.group(1))).strip()
        if '\u00b7' in t:
            main, _, sub = t.partition('\u00b7')
            info['title'], info['sub'] = main.strip(), sub.strip()
        else:
            info['title'] = t
    for key in ('subject', 'chapter', 'knowledge', 'source', 'type', 'number', 'tags', 'method', 'date'):
        mm = re.search(r'<meta\s+name=["\']' + key + r'["\']\s+content=["\'](.*?)["\']', head, re.I)
        if mm:
            info[key] = html.unescape(mm.group(1)).strip()
    return info


def scan_lessons():
    items = []
    for d in sorted(glob.glob(os.path.join(LESSONS_DIR, '*'))) or []:
        if not os.path.isdir(d):
            continue
        idx_path = os.path.join(d, 'index.html')
        if not os.path.exists(idx_path):
            continue
        name = os.path.basename(d)
        num = re.match(r'(\d+)', name)
        order = int(num.group(1)) if num else 10 ** 9
        meta = extract_meta(idx_path)
        mtime = datetime.fromtimestamp(os.path.getmtime(idx_path)).strftime('%Y-%m-%d')
        # 制作日期：优先课件内 meta，回退文件 mtime
        cdate = meta.get('date') or mtime
        items.append({
            'order': order,
            'num': num.group(1).zfill(2) if num else '',
            'dir': name,
            'link': 'lessons/' + name + '/',
            'title': meta['title'],
            'sub': meta['sub'] or '互动解题课件',
            'date': cdate,
            'subject': meta['subject'] or '未分类',
            'chapter': meta['chapter'] or '未分类',
            'knowledge': meta['knowledge'] or '未分类',
            'method': meta.get('method') or '未标注',
            'source': meta['source'] or '',
            'type': meta['type'] or '',
            'number': meta['number'] or '',
            'tags': meta['tags'] or '',
            'tags_list': [t.strip() for t in (meta['tags'] or '').split(';') if t.strip()],
        })
    items.sort(key=lambda x: x['order'])
    for i, it in enumerate(items, 1):
        if not it['num']:
            it['num'] = str(i).zfill(2)
    return items


CARD_TMPL = """    <a class="card" href="{link}" target="_blank" rel="noopener" data-subject="{subject}" data-chapter="{chapter}" data-knowledge="{knowledge}" data-method="{method}" data-date="{date}" data-tags="{tags_attr}">
      <span class="badge">{number}</span>
      <div class="card-body">
        <h3>{title}</h3>
        <p class="sub">{sub}</p>
        <div class="tags">{tags}</div>
        {source_html}
        <span class="go">打开课件 \u2192</span>
      </div>
    </a>"""


def check_opts(values, filter_key):
    parts = []
    for v in values:
        ev = html.escape(v)
        parts.append(f'<label class="popup-option"><input type="checkbox" data-filter="{filter_key}" value="{ev}">{ev}</label>')
    return ''.join(parts)


PAGE_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>\u6615\u8a00\u89e3\u9898\u8bfe\u4ef6\u5e93 \u00b7 \u4e92\u52a8\u8bfe\u4ef6\u5bfc\u822a</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family:'PingFang SC','Microsoft YaHei','Segoe UI',system-ui,sans-serif;
    background:
      radial-gradient(900px 420px at 8% -4%, rgba(91,124,250,.10), transparent 60%),
      radial-gradient(760px 380px at 96% -6%, rgba(45,208,180,.12), transparent 60%),
      linear-gradient(160deg,#eef6ff,#f2fdf7);
    background-attachment:fixed; color:#1f2d3d; min-height:100vh; padding:28px 18px 60px;
  }}
  .wrap {{ max-width:1080px; margin:0 auto; }}
  .hero {{
    background:linear-gradient(120deg,#5b7cfa,#4f8ef7 45%,#2fd0b4,#57d98d);
    border-radius:22px; padding:44px 40px 40px; color:#fff;
    box-shadow:0 18px 44px -18px rgba(47,120,240,.55);
  }}
  .hero .tag {{
    display:inline-block; background:rgba(255,255,255,.22); border:1px solid rgba(255,255,255,.35);
    font-size:13px; padding:4px 12px; border-radius:999px; margin-bottom:16px; letter-spacing:1px;
  }}
  .hero a.mgmt {{ margin-left:12px; color:#fff; text-decoration:none; font-size:13px; opacity:.8; border-bottom:1px dashed rgba(255,255,255,.5); }}
  .hero a.mgmt:hover {{ opacity:1; }}
  .hero h1 {{ font-size:34px; font-weight:700; letter-spacing:1px; }}
  .hero p {{ margin-top:12px; font-size:15px; opacity:.95; line-height:1.7; max-width:680px; }}
  .stat {{ display:flex; gap:26px; margin-top:24px; flex-wrap:wrap; }}
  .stat div {{ background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.3); border-radius:14px; padding:10px 18px; }}
  .stat b {{ font-size:22px; display:block; }}
  .stat span {{ font-size:12px; opacity:.92; }}
  .filters {{
    margin-top:22px; background:#fff; border:1px solid #e3edf7; border-radius:18px; padding:18px 20px;
    box-shadow:0 10px 30px -12px rgba(31,66,135,.16);
    display:flex; flex-wrap:wrap; gap:14px; align-items:flex-end;
  }}
  .fld {{ display:flex; flex-direction:column; gap:5px; flex:1 1 160px; }}
  .fld label {{ font-size:12px; color:#5c7185; font-weight:600; }}
  .fld.search {{ flex:2 1 240px; }}
  .fld.search input {{
    padding:9px 12px; border:1.5px solid #d6e4f2; border-radius:10px; font-size:14px;
    background:#f8fbff; color:#1f2d3d; font-family:inherit;
  }}
  .fld input:focus {{ outline:none; border-color:#4f8ef7; }}
  .popup-filter {{ position:relative; }}
  .filter-btn {{
    padding:9px 12px; border:1.5px solid #d6e4f2; border-radius:10px; font-size:14px;
    background:#f8fbff; color:#1f2d3d; cursor:pointer; font-family:inherit;
    width:100%; text-align:left; display:flex; justify-content:space-between; align-items:center; gap:6px;
  }}
  .filter-btn:hover {{ border-color:#4f8ef7; }}
  .filter-btn .cnt {{ background:#4f8ef7; color:#fff; border-radius:999px; padding:1px 8px; font-size:12px; min-width:20px; text-align:center; flex:none; }}
  .filter-btn .cnt.zero {{ background:#c5d4e8; }}
  .popup {{
    position:absolute; top:calc(100% + 4px); left:0; min-width:240px; max-width:340px;
    background:#fff; border:1px solid #d6e4f2; border-radius:12px;
    box-shadow:0 12px 32px -8px rgba(31,66,135,.2); z-index:200; display:none; padding:10px;
  }}
  .popup.open {{ display:block; }}
  .popup-search {{
    width:100%; padding:7px 10px; border:1px solid #d6e4f2; border-radius:8px; font-size:13px;
    margin-bottom:8px; font-family:inherit;
  }}
  .popup-search:focus {{ outline:none; border-color:#4f8ef7; }}
  .popup-options {{ max-height:220px; overflow-y:auto; }}
  .popup-option {{
    display:flex; align-items:center; gap:8px; padding:5px 6px; cursor:pointer;
    font-size:13px; border-radius:6px; color:#1f2d3d;
  }}
  .popup-option:hover {{ background:#f0f5ff; }}
  .popup-option input {{ margin:0; }}
  .popup-actions {{ display:flex; gap:8px; margin-top:8px; padding-top:8px; border-top:1px solid #eef2f8; }}
  .popup-actions button {{ padding:5px 14px; border:1px solid #d6e4f2; border-radius:8px; font-size:12px; cursor:pointer; background:#fff; color:#5c7185; font-family:inherit; }}
  .popup-actions button:hover {{ background:#f0f5ff; color:#2a6df4; }}
  .popup-options.drange {{ display:flex; flex-direction:column; gap:8px; }}
  .popup-options .dr-row {{ display:flex; align-items:center; gap:8px; justify-content:space-between; }}
  .popup-options .dr-row select {{ flex:1; padding:6px 8px; border:1px solid #d6e4f2; border-radius:8px; font-size:12.5px; background:#fff; color:#1f2d3d; font-family:inherit; }}
  .reset-btn {{
    background:#fff; color:#4f8ef7; border:1.5px solid #4f8ef7; border-radius:10px;
    padding:9px 16px; font-size:13px; cursor:pointer; font-weight:600; height:38px;
  }}
  .reset-btn:hover {{ background:#4f8ef7; color:#fff; }}
  .result-info {{ margin:14px 4px 0; font-size:13px; color:#5c7185; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:18px; margin-top:16px; }}
  .card {{
    display:flex; gap:14px; background:#fff; border:1px solid #e3edf7; border-radius:20px;
    padding:20px 18px; text-decoration:none; color:inherit;
    box-shadow:0 10px 30px -12px rgba(31,66,135,.16);
    transition:transform .18s ease, box-shadow .18s ease;
  }}
  .card:hover {{ transform:translateY(-3px); box-shadow:0 16px 36px -12px rgba(31,66,135,.26); }}
  .badge {{
    flex:none; width:46px; height:46px; border-radius:50%;
    background:linear-gradient(135deg,#4f8ef7,#22c3a6); color:#fff;
    display:flex; align-items:center; justify-content:center;
    font-size:11px; font-weight:600;
  }}
  .card-body {{ min-width:0; flex:1; }}
  .card-body h3 {{ font-size:16px; color:#1f2d3d; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
  .card-body .sub {{ font-size:13px; color:#5c7185; margin-top:5px; line-height:1.5; }}
  .tags {{ display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }}
  .tag-chip {{ font-size:11px; padding:2px 9px; border-radius:999px; background:#eef3ff; color:#2a6df4; }}
  .tag-chip.k {{ background:#ecfdf6; color:#1a9e7a; }}
  .tag-chip.c {{ background:#fff4e6; color:#d98512; }}
  .src {{ font-size:11px; color:#93a7ba; margin-top:6px; }}
  .go {{
    display:inline-block; margin-top:10px; font-size:13px; color:#fff;
    background:linear-gradient(120deg,#4f8ef7,#22c3a6);
    padding:5px 14px; border-radius:999px;
  }}
  .empty {{ grid-column:1/-1; text-align:center; padding:40px; color:#93a7ba; }}
  .foot {{ text-align:center; margin-top:34px; font-size:12px; color:#93a7ba; }}
  .foot a {{ color:#4f8ef7; text-decoration:none; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <span class="tag">\u4e92\u52a8\u89e3\u9898\u8bfe\u4ef6\u5e93 \u00b7 \u5355\u6587\u4ef6\u79bb\u7ebf\u53ef\u7528</span>
    <a class="mgmt" href="manage.html">\u6807\u7b7e\u7ba1\u7406 \u2192</a>
    <h1>\u6615\u8a00\u89e3\u9898\u8bfe\u4ef6\u5e93</h1>
    <p>Fresh Gradient \u6559\u80b2\u98ce\u4e92\u52a8\u8bfe\u4ef6\uff1a\u9010\u6b65\u63a8\u5bfc\u3001\u5373\u65f6\u53cd\u9988\u3001KaTeX \u516c\u5f0f\u7f16\u8bd1\uff0c\u5168\u90e8\u5185\u5d4c\u5355\u6587\u4ef6\uff0c\u53ef\u79bb\u7ebf\u6253\u5f00\u3002\u652f\u6301\u6309<b>\u5b66\u79d1 / \u7ae0\u8282 / \u77e5\u8bc6\u70b9 / \u89e3\u6cd5 / \u65e5\u671f</b>\u5f39\u7a97\u591a\u9009\u7b5b\u9009\u3002</p>
    <div class="stat">
      <div><b>{count}</b><span>\u4e2a\u8bfe\u4ef6</span></div>
      <div><b>{subject_count}</b><span>\u4e2a\u5b66\u79d1</span></div>
      <div><b>{chapter_count}</b><span>\u4e2a\u7ae0\u8282</span></div>
      <div><b>{tag_count}</b><span>\u4e2a\u6807\u7b7e</span></div>
    </div>
  </div>

  <div class="filters">
    <div class="fld">
      <label>\u5b66\u79d1</label>
      <div class="popup-filter">
        <button class="filter-btn" type="button" id="btnSubject">\u5b66\u79d1 <span class="cnt zero" id="cntSubject">0</span></button>
        <div class="popup" id="popupSubject">
          <input class="popup-search" placeholder="\u641c\u7d22\u2026" id="searchSubject">
          <div class="popup-options">{subject_checks}</div>
          <div class="popup-actions">
            <button type="button" data-all="subject">\u2611 \u5168\u9009</button>
            <button type="button" data-clear="subject">\u6e05\u9664</button>
            <button type="button" data-close="popupSubject">\u786e\u5b9a</button>
          </div>
        </div>
      </div>
    </div>
    <div class="fld">
      <label>\u6240\u5c5e\u7ae0\u8282</label>
      <div class="popup-filter">
        <button class="filter-btn" type="button" id="btnChapter">\u7ae0\u8282 <span class="cnt zero" id="cntChapter">0</span></button>
        <div class="popup" id="popupChapter">
          <input class="popup-search" placeholder="\u641c\u7d22\u2026" id="searchChapter">
          <div class="popup-options">{chapter_checks}</div>
          <div class="popup-actions">
            <button type="button" data-all="chapter">\u2611 \u5168\u9009</button>
            <button type="button" data-clear="chapter">\u6e05\u9664</button>
            <button type="button" data-close="popupChapter">\u786e\u5b9a</button>
          </div>
        </div>
      </div>
    </div>
    <div class="fld">
      <label>\u77e5\u8bc6\u70b9</label>
      <div class="popup-filter">
        <button class="filter-btn" type="button" id="btnKnowledge">\u77e5\u8bc6\u70b9 <span class="cnt zero" id="cntKnowledge">0</span></button>
        <div class="popup" id="popupKnowledge">
          <input class="popup-search" placeholder="\u641c\u7d22\u2026" id="searchKnowledge">
          <div class="popup-options">{knowledge_checks}</div>
          <div class="popup-actions">
            <button type="button" data-all="knowledge">\u2611 \u5168\u9009</button>
            <button type="button" data-clear="knowledge">\u6e05\u9664</button>
            <button type="button" data-close="popupKnowledge">\u786e\u5b9a</button>
          </div>
        </div>
      </div>
    </div>
    <div class="fld">
      <label>\u89e3\u6cd5</label>
      <div class="popup-filter">
        <button class="filter-btn" type="button" id="btnMethod">\u89e3\u6cd5 <span class="cnt zero" id="cntMethod">0</span></button>
        <div class="popup" id="popupMethod">
          <input class="popup-search" placeholder="\u641c\u7d22\u2026" id="searchMethod">
          <div class="popup-options">{method_checks}</div>
          <div class="popup-actions">
            <button type="button" data-all="method">\u2611 \u5168\u9009</button>
            <button type="button" data-clear="method">\u6e05\u9664</button>
            <button type="button" data-close="popupMethod">\u786e\u5b9a</button>
          </div>
        </div>
      </div>
    </div>
    <div class="fld">
      <label>\u5236\u4f5c\u65e5\u671f</label>
      <div class="popup-filter">
        <button class="filter-btn" type="button" id="btnDate">\u65e5\u671f <span class="cnt zero" id="cntDate">0</span></button>
        <div class="popup" id="popupDate">
          <div class="popup-options drange">
            <label class="popup-option dr-row"><span>\u4ece</span><select id="dateFrom"><option value="">\u4e0d\u9650</option>{date_options}</select></label>
            <label class="popup-option dr-row"><span>\u81f3</span><select id="dateTo"><option value="">\u4e0d\u9650</option>{date_options}</select></label>
          </div>
          <div class="popup-actions">
            <button type="button" id="dateClear">\u6e05\u9664</button>
            <button type="button" data-close="popupDate">\u786e\u5b9a</button>
          </div>
        </div>
      </div>
    </div>
    <div class="fld search">
      <label>\u641c\u7d22\u6807\u9898/\u6765\u6e90</label>
      <input id="fSearch" placeholder="\u8f93\u5165\u5173\u952e\u5b57\u2026" autocomplete="off">
    </div>
    <button class="reset-btn" id="fReset" type="button">\u91cd\u7f6e</button>
  </div>
  <div class="result-info" id="resultInfo">\u5171 {count} \u4e2a\u8bfe\u4ef6</div>

  <div class="grid" id="grid">
{cards}
  </div>
  <div class="foot"><a href="manage.html">\u6807\u7b7e\u7ba1\u7406</a> \u00b7 mcjc4 \u00b7 GitHub Pages \u00b7 \u9875\u9762\u751f\u6210\u4e8e {date}</div>
</div>
<script>
(function(){{
  var grid=document.getElementById('grid');
  var cards=Array.from(grid.querySelectorAll('.card'));
  var fQ=document.getElementById('fSearch');
  var info=document.getElementById('resultInfo');
  var sets={{subject:new Set(),chapter:new Set(),knowledge:new Set(),method:new Set(),date:new Set()}};
  var cntIds={{subject:'cntSubject',chapter:'cntChapter',knowledge:'cntKnowledge',method:'cntMethod',date:'cntDate'}};
  var dateFrom=document.getElementById('dateFrom');
  var dateTo=document.getElementById('dateTo');

  function updateDateCnt(){{
    var n=(dateFrom.value?1:0)+(dateTo.value?1:0);
    var el=document.getElementById('cntDate');
    if(n>0){{el.textContent=n;el.className='cnt';}}else{{el.textContent='0';el.className='cnt zero';}}
  }}

  function updateCnt(f){{
    var n=sets[f].size;
    var el=document.getElementById(cntIds[f]);
    el.textContent=n;
    el.className=n===0?'cnt zero':'cnt';
  }}

  function apply(){{
    var q=fQ.value.trim().toLowerCase();
    var n=0;
    cards.forEach(function(card){{
      var okS=sets.subject.size===0||sets.subject.has(card.dataset.subject);
      var okC=sets.chapter.size===0||sets.chapter.has(card.dataset.chapter);
      var okK=sets.knowledge.size===0||sets.knowledge.has(card.dataset.knowledge);
      var okM=sets.method.size===0||sets.method.has(card.dataset.method);
      var dv=card.dataset.date||'';
      var okD=(!dateFrom.value||dv>=dateFrom.value)&&(!dateTo.value||dv<=dateTo.value);
      var okQ=!q||(card.textContent||'').toLowerCase().indexOf(q)>=0;
      var show=okS&&okC&&okK&&okM&&okD&&okQ;
      card.style.display=show?'':'none';
      if(show)n++;
    }});
    info.textContent='\u5171 '+n+' \u4e2a\u8bfe\u4ef6';
    var empty=document.getElementById('emptyHint');
    if(n===0){{
      if(!empty){{empty=document.createElement('div');empty.className='empty';empty.id='emptyHint';empty.textContent='\u6ca1\u6709\u7b26\u5408\u6761\u4ef6\u7684\u8bfe\u4ef6\uff0c\u8bd5\u8bd5\u6362\u4e2a\u7b5b\u9009\u6761\u4ef6\u3002';grid.appendChild(empty);}}
    }}else{{if(empty)empty.remove();}}
  }}

  document.querySelectorAll('.filter-btn').forEach(function(btn){{
    btn.addEventListener('click',function(e){{
      e.stopPropagation();
      var popup=btn.nextElementSibling;
      var isOpen=popup.classList.contains('open');
      document.querySelectorAll('.popup.open').forEach(function(p){{p.classList.remove('open');}});
      if(!isOpen)popup.classList.add('open');
      var search=popup.querySelector('.popup-search');
      if(search)setTimeout(function(){{search.focus();}},0);
    }});
  }});
  document.addEventListener('click',function(e){{
    if(!e.target.closest('.popup-filter'))
      document.querySelectorAll('.popup.open').forEach(function(p){{p.classList.remove('open');}});
  }});
  document.querySelectorAll('.popup').forEach(function(p){{
    p.addEventListener('click',function(e){{e.stopPropagation();}});
  }});

  document.querySelectorAll('.popup-option input[type="checkbox"]').forEach(function(cb){{
    cb.addEventListener('change',function(){{
      var f=cb.dataset.filter,v=cb.value;
      if(cb.checked)sets[f].add(v);else sets[f].delete(v);
      updateCnt(f);
      apply();
    }});
  }});

  document.querySelectorAll('.popup-search').forEach(function(input){{
    input.addEventListener('input',function(){{
      var q=this.value.trim().toLowerCase();
      this.closest('.popup').querySelectorAll('.popup-option').forEach(function(opt){{
        opt.style.display=(!q||opt.textContent.toLowerCase().indexOf(q)>=0)?'':'none';
      }});
    }});
  }});

  document.querySelectorAll('.popup-actions button[data-clear]').forEach(function(btn){{
    btn.addEventListener('click',function(){{
      var f=btn.dataset.clear;
      sets[f].clear();
      document.querySelectorAll('.popup-option input[data-filter="'+f+'"]').forEach(function(cb){{cb.checked=false;}});
      updateCnt(f);
      apply();
    }});
  }});
  document.querySelectorAll('.popup-actions button[data-all]').forEach(function(btn){{
    btn.addEventListener('click',function(){{
      var f=btn.dataset.all;
      sets[f].clear();
      document.querySelectorAll('.popup-option input[data-filter="'+f+'"]').forEach(function(cb){{
        cb.checked=true;sets[f].add(cb.value);
      }});
      updateCnt(f);apply();
    }});
  }});
  document.querySelectorAll('.popup-actions button[data-close]').forEach(function(btn){{
    btn.addEventListener('click',function(){{
      document.getElementById(btn.dataset.close).classList.remove('open');
    }});
  }});

  dateFrom.addEventListener('change',function(){{updateDateCnt();apply();}});
  dateTo.addEventListener('change',function(){{updateDateCnt();apply();}});
  document.getElementById('dateClear').addEventListener('click',function(){{
    dateFrom.value='';dateTo.value='';updateDateCnt();apply();
  }});

  fQ.addEventListener('input',apply);
  document.getElementById('fReset').addEventListener('click',function(){{
    ['subject','chapter','knowledge','method','date'].forEach(function(f){{
      sets[f].clear();
      document.querySelectorAll('.popup-option input[data-filter="'+f+'"]').forEach(function(cb){{cb.checked=false;}});
      updateCnt(f);
    }});
    dateFrom.value='';dateTo.value='';updateDateCnt();
    fQ.value='';apply();
  }});
}})();
</script>
</body>
</html>"""


# manage.html uses .replace() not .format(), so braces are literal
MANAGE_TMPL = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>标签管理 · 昕言解题课件库</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'PingFang SC','Microsoft YaHei',system-ui,sans-serif; background:linear-gradient(160deg,#eef6ff,#f2fdf7); background-attachment:fixed; color:#1f2d3d; min-height:100vh; padding:24px 16px 60px; }
  .wrap { max-width:1100px; margin:0 auto; }
  .back { display:inline-flex; align-items:center; gap:6px; background:#fff; border:1px solid #d6e4f2; border-radius:10px; padding:7px 14px; font-size:13px; color:#2a6df4; text-decoration:none; font-weight:600; margin-bottom:14px; box-shadow:0 4px 12px -6px rgba(31,66,135,.2); }
  .back:hover { background:#4f8ef7; color:#fff; }
  .hero { background:linear-gradient(120deg,#5b7cfa,#4f8ef7 45%,#2fd0b4); border-radius:22px; padding:36px 32px; color:#fff; box-shadow:0 18px 44px -18px rgba(47,120,240,.55); margin-bottom:20px; }
  .hero h1 { font-size:28px; font-weight:700; }
  .hero p { margin-top:10px; font-size:14px; opacity:.95; line-height:1.7; }
  .toolbar { display:flex; gap:12px; margin-bottom:16px; flex-wrap:wrap; align-items:center; }
  .toolbar input { padding:9px 14px; border:1.5px solid #d6e4f2; border-radius:10px; font-size:14px; background:#fff; font-family:inherit; flex:1 1 200px; }
  .toolbar input:focus { outline:none; border-color:#4f8ef7; }
  .btn { padding:9px 18px; border:none; border-radius:10px; font-size:14px; cursor:pointer; font-weight:600; font-family:inherit; }
  .btn-primary { background:linear-gradient(120deg,#4f8ef7,#22c3a6); color:#fff; }
  .btn-secondary { background:#fff; color:#4f8ef7; border:1.5px solid #4f8ef7; }
  .btn:hover { opacity:.9; }
  .tbl-wrap { background:#fff; border:1px solid #e3edf7; border-radius:18px; box-shadow:0 10px 30px -12px rgba(31,66,135,.16); overflow:hidden; overflow-x:auto; }
  table { width:100%; border-collapse:collapse; min-width:700px; }
  th { background:#f8fbff; padding:12px 14px; text-align:left; font-size:12px; color:#5c7185; font-weight:600; border-bottom:1px solid #e3edf7; white-space:nowrap; }
  td { padding:10px 14px; font-size:13px; border-bottom:1px solid #f0f5ff; vertical-align:middle; }
  tr:hover { background:#fafcff; }
  .num { font-weight:600; color:#4f8ef7; white-space:nowrap; }
  .title-cell { max-width:200px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .tag-input { width:100%; padding:6px 10px; border:1px solid #e0e8f0; border-radius:8px; font-size:13px; font-family:inherit; }
  .tag-input:focus { outline:none; border-color:#4f8ef7; box-shadow:0 0 0 2px rgba(79,142,247,.15); }
  .tag-input.dirty { border-color:#d98512; background:#fff8f0; }
  .script-box { margin-top:20px; }
  .script-box textarea { width:100%; min-height:220px; padding:14px; border:1.5px solid #d6e4f2; border-radius:12px; font-family:'Consolas','Monaco',monospace; font-size:12px; line-height:1.6; resize:vertical; background:#f8fbff; }
  .copy-bar { display:flex; gap:10px; margin-top:10px; align-items:center; }
  .copy-msg { font-size:13px; color:#1a9e7a; opacity:0; transition:opacity .3s; }
  .copy-msg.show { opacity:1; }
  .foot { text-align:center; margin-top:30px; font-size:12px; color:#93a7ba; }
  .foot a { color:#4f8ef7; text-decoration:none; }
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="index.html">← 返回导航页</a>
  <div class="hero">
    <h1>标签管理</h1>
    <p>编辑每个课件的标签（分号分隔），点击「生成更新脚本」，复制到本地运行即可批量更新。</p>
  </div>
  <div class="toolbar">
    <input id="searchBox" placeholder="搜索课件标题/编号/标签…" autocomplete="off">
    <button class="btn btn-secondary" id="resetSearchBtn">显示全部</button>
    <button class="btn btn-primary" id="genScriptBtn">生成更新脚本</button>
  </div>
  <div class="tbl-wrap">
    <table>
      <thead><tr>
        <th>编号</th><th>标题</th><th>学科</th><th>章节</th><th>知识点</th><th>标签（分号分隔，可编辑）</th>
      </tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
  <div class="script-box" id="scriptBox" style="display:none">
    <textarea id="scriptArea" readonly></textarea>
    <div class="copy-bar">
      <button class="btn btn-primary" id="copyBtn">复制脚本</button>
      <span class="copy-msg" id="copyMsg">已复制！</span>
    </div>
  </div>
  <div class="foot"><a href="index.html">返回导航</a> · mcjc4 · GitHub Pages</div>
</div>
<script>
var data = __DATA_JSON__;

var tbody = document.getElementById('tbody');
var searchBox = document.getElementById('searchBox');

function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function render(filter) {
  filter = filter || '';
  tbody.innerHTML = '';
  data.forEach(function(it) {
    if (filter) {
      var hay = (it.number + ' ' + it.title + ' ' + it.subject + ' ' + it.chapter + ' ' + it.knowledge + ' ' + it.tags).toLowerCase();
      if (hay.indexOf(filter) < 0) return;
    }
    var tr = document.createElement('tr');
    tr.innerHTML = '<td class="num">' + esc(it.number) + '</td>'
      + '<td class="title-cell" title="' + esc(it.title) + '">' + esc(it.title) + '</td>'
      + '<td>' + esc(it.subject) + '</td>'
      + '<td>' + esc(it.chapter) + '</td>'
      + '<td>' + esc(it.knowledge) + '</td>'
      + '<td><input class="tag-input" data-dir="' + esc(it.dir) + '" value="' + esc(it.tags) + '" data-orig="' + esc(it.tags) + '"></td>';
    tbody.appendChild(tr);
  });
  tbody.querySelectorAll('.tag-input').forEach(function(inp) {
    inp.addEventListener('input', function() {
      inp.classList.toggle('dirty', inp.value !== inp.dataset.orig);
    });
  });
}

searchBox.addEventListener('input', function() { render(this.value.trim().toLowerCase()); });
document.getElementById('resetSearchBtn').addEventListener('click', function() { searchBox.value = ''; render(''); });

document.getElementById('genScriptBtn').addEventListener('click', function() {
  var dirty = {};
  tbody.querySelectorAll('.tag-input').forEach(function(inp) {
    if (inp.value !== inp.dataset.orig) {
      dirty[inp.dataset.dir] = inp.value;
    }
  });
  var keys = Object.keys(dirty);
  if (keys.length === 0) {
    document.getElementById('scriptArea').value = '# 没有检测到修改。请先编辑一些标签再生成脚本。';
  } else {
    var lines = [];
    lines.push('#!/usr/bin/env python3');
    lines.push('# -*- coding: utf-8 -*-');
    lines.push('"""标签批量更新脚本 - 由 manage.html 生成"""');
    lines.push('import re, os');
    lines.push('');
    lines.push('base = r\'C:\\Users\\admin\\WorkBuddy\\courseware-site\\lessons\'');
    lines.push('updates = {');
    keys.forEach(function(d) {
      var v = dirty[d].replace(/\\/g, '\\\\').replace(/'/g, "\\'");
      lines.push("    '" + d + "': '" + v + "',");
    });
    lines.push('}');
    lines.push('');
    lines.push("changed = 0");
    lines.push("for dirname, new_tags in updates.items():");
    lines.push("    fpath = os.path.join(base, dirname, 'index.html')");
    lines.push("    if not os.path.exists(fpath):");
    lines.push("        print(f'  SKIP: {dirname} (file not found)')");
    lines.push("        continue");
    lines.push("    with open(fpath, 'r', encoding='utf-8') as f:");
    lines.push("        content = f.read()");
    lines.push("    new_meta = '  <meta name=\"tags\" content=\"' + new_tags + '\">'");
    lines.push("    if re.search(r'<meta\\s+name=[\"\\']tags[\"\\']', content):");
    lines.push("        content = re.sub(r'<meta\\s+name=[\"\\']tags[\"\\']\\s+content=[\"\\'].*?[\"\\']', new_meta, content)");
    lines.push("    else:");
    lines.push("        metas = list(re.finditer(r'<meta\\s+[^>]*>', content))");
    lines.push("        if metas:");
    lines.push("            pos = metas[-1].end()");
    lines.push("            content = content[:pos] + '\\n' + new_meta + content[pos:]");
    lines.push("    with open(fpath, 'w', encoding='utf-8') as f:");
    lines.push("        f.write(content)");
    lines.push("    changed += 1");
    lines.push("    print(f'  Updated: {dirname}')");
    lines.push('');
    lines.push("print(f'\\nDone! {changed} files updated.')");
    lines.push("print('Now run: python gen_index.py')");
    document.getElementById('scriptArea').value = lines.join('\n');
  }
  document.getElementById('scriptBox').style.display = 'block';
});

document.getElementById('copyBtn').addEventListener('click', function() {
  var ta = document.getElementById('scriptArea');
  ta.select();
  document.execCommand('copy');
  var msg = document.getElementById('copyMsg');
  msg.classList.add('show');
  setTimeout(function() { msg.classList.remove('show'); }, 2000);
});

render('');
</script>
</body>
</html>'''


def main():
    items = scan_lessons()
    subjects = sorted({it['subject'] for it in items if it['subject']})
    chapters = sorted({it['chapter'] for it in items if it['chapter']})
    knowledges = sorted({it['knowledge'] for it in items if it['knowledge']})
    methods = sorted({it['method'] for it in items if it['method']})
    dates_asc = sorted({it['date'] for it in items if it['date']})
    all_tags = set()
    for it in items:
        for t in it.get('tags_list', []):
            all_tags.add(t)
    all_tags = sorted(all_tags)

    cards = []
    for it in items:
        tags = (f'<span class="tag-chip">{html.escape(it["subject"])}</span>'
                f'<span class="tag-chip c">{html.escape(it["chapter"])}</span>'
                f'<span class="tag-chip k">{html.escape(it["knowledge"])}</span>')
        if it.get('tags_list'):
            for tg in it['tags_list']:
                tags += f'<span class="tag-chip" style="background:#f0f0ff;color:#555">{html.escape(tg)}</span>'
        if it['type']:
            tags += f'<span class="tag-chip" style="background:#f3e8ff;color:#8b5cf6">{html.escape(it["type"])}</span>'
        tags += f'<span class="tag-chip" style="background:#fff7e6;color:#b45309">\U0001f4c5 {html.escape(it["date"])}</span>'
        source_html = f'<div class="src">{html.escape(it["source"])}</div>' if it['source'] else ''
        cards.append(CARD_TMPL.format(
            link=it['link'], number=it['number'] or it['num'], title=html.escape(it['title']),
            sub=html.escape(it['sub']), tags=tags, source_html=source_html,
            subject=html.escape(it['subject']), chapter=html.escape(it['chapter']),
            knowledge=html.escape(it['knowledge']),
            method=html.escape(it['method']), date=html.escape(it['date']),
            tags_attr=html.escape(';'.join(it.get('tags_list', []))),
        ))
    cards_html = '\n'.join(cards) if cards else '    <div class="empty">暂无课件</div>'

    today = datetime.now().strftime('%Y-%m-%d')
    page = PAGE_TMPL.format(
        count=len(items), subject_count=len(subjects), chapter_count=len(chapters),
        tag_count=len(all_tags),
        subject_checks=check_opts(subjects, 'subject'),
        chapter_checks=check_opts(chapters, 'chapter'),
        knowledge_checks=check_opts(knowledges, 'knowledge'),
        method_checks=check_opts(methods, 'method'),
        date_options=''.join(f'<option value="{d}">{d}</option>' for d in dates_asc),
        cards=cards_html, date=today,
    )
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(page)
    print(f'OK: index.html ({len(page)/1024:.0f} KB) - {len(items)} courseware')

    # generate manage.html
    manage_data = json.dumps([{
        'dir': it['dir'],
        'number': it['number'] or it['num'],
        'title': it['title'],
        'subject': it['subject'],
        'chapter': it['chapter'],
        'knowledge': it['knowledge'],
        'tags': it['tags'],
    } for it in items], ensure_ascii=False, indent=2)

    manage_html = MANAGE_TMPL.replace('__DATA_JSON__', manage_data)
    with open(MANAGE_OUT, 'w', encoding='utf-8') as f:
        f.write(manage_html)
    print(f'OK: manage.html ({len(manage_html)/1024:.0f} KB)')


if __name__ == '__main__':
    main()