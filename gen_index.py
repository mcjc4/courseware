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


def read_cmeta(path):
    """读课件内 <script id="c-meta"> 静态清单（统计联动数据源）。
    注意：KaTeX 内嵌样式块 ~280KB，c-meta 在其后，必须全文读取"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            head = f.read()
        m = re.search(r'<script type="application/json" id="c-meta">(.*?)</script>', head, re.S)
        if m:
            return json.loads(m.group(1))
    except Exception:
        pass
    return None


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
        cm = read_cmeta(idx_path) or {}
        cid = cm.get('id') or ('course_' + re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_'))
        cm_title = cm.get('title') or ''
        # 41-47 类「45 · 题名」被按 · 分段成纯数字标题，用 c-meta 完整题名修正
        title = cm_title if (meta['title'].isdigit() and cm_title) else meta['title']
        sub = meta['sub'] or '互动解题课件'
        if title == cm_title and cm_title and '\u00b7' in cm_title and meta['title'].isdigit():
            sub = cm_title.partition('\u00b7')[2].strip() or sub
            title = cm_title.partition('\u00b7')[0].strip()
        items.append({
            'order': order,
            'num': num.group(1).zfill(2) if num else '',
            'dir': name,
            'link': 'lessons/' + name + '/',
            'title': title,
            'sub': sub,
            'cid': cid,
            'points': cm.get('points', []),
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


CARD_TMPL = """    <a class="card" href="{link}" target="_blank" rel="noopener" data-subject="{subject}" data-chapter="{chapter}" data-knowledge="{knowledge}" data-method="{method}" data-date="{date}" data-num="{num_attr}" data-cid="{cid}" data-tags="{tags_attr}">
      <span class="badge">{number}</span>
      <div class="card-body">
        <h3>{title}</h3>
        <p class="sub">{sub}</p>
        <div class="tags">{tags}</div>
        <div class="cstat-line"><span class="c-badge st-new">⚪ 未训练</span></div>
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
  .fld input:focus, .fld select:focus {{ outline:none; border-color:#4f8ef7; }}
  .fld select.sort-select {{
    padding:9px 10px; border:1.5px solid #d6e4f2; border-radius:10px; font-size:14px;
    background:#f8fbff; color:#1f2d3d; font-family:inherit; cursor:pointer;
  }}
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
  .popup-options .dr-row input[type="date"] {{ flex:1; padding:5px 6px; border:1px solid #d6e4f2; border-radius:8px; font-size:12.5px; background:#fff; color:#1f2d3d; font-family:inherit; }}
  .active-filters {{ display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:12px 0 2px; min-height:26px; }}
  .active-filters .af-label {{ font-size:12px; color:#7c8aa0; font-weight:600; }}
  .af-chip {{ display:inline-flex; align-items:center; gap:6px; padding:4px 6px 4px 12px; border-radius:999px; background:#eef4ff; color:#1d4ed8; border:1px solid #c7dbff; font-size:12px; font-weight:600; }}
  .af-chip .x {{ cursor:pointer; width:18px; height:18px; line-height:16px; text-align:center; border-radius:50%; background:#dce7ff; color:#1e40af; font-size:12px; user-select:none; }}
  .af-chip .x:hover {{ background:#1d4ed8; color:#fff; }}
  .af-chip .x::before {{ content:"×"; }}
  .reset-btn {{
    background:#fff; color:#4f8ef7; border:1.5px solid #4f8ef7; border-radius:10px;
    padding:9px 16px; font-size:13px; cursor:pointer; font-weight:600; height:38px;
  }}
  .reset-btn:hover {{ background:#4f8ef7; color:#fff; }}
  .result-info {{ margin:14px 4px 0; font-size:13px; color:#5c7185; }}
  .train-btn {{
    margin-left:10px; border:none; cursor:pointer; font-size:13px; font-weight:600; color:#fff;
    background:linear-gradient(120deg,#4f8ef7,#22c3a6); padding:6px 16px; border-radius:999px;
    box-shadow:0 6px 16px -6px rgba(31,142,247,.5); transition:transform .15s;
  }}
  .train-btn:hover {{ transform:translateY(-1px); }}
  /* ===== 专题练面板 ===== */
  #trainOverlay {{ display:none; position:fixed; inset:0; z-index:999; background:rgba(23,38,58,.62); }}
  #trainOverlay.open {{ display:flex; align-items:center; justify-content:center; }}
  .train-panel {{
    width:min(680px, 92vw); max-height:88vh; overflow:auto; background:#fff; border-radius:24px;
    box-shadow:0 30px 80px -20px rgba(15,40,90,.5); display:flex; flex-direction:column;
  }}
  .train-head {{ display:flex; align-items:center; justify-content:space-between; padding:16px 22px 0; }}
  .train-progress {{ font-size:15px; font-weight:700; color:#1f2d3d; }}
  .train-progress small {{ color:#7c8aa0; font-weight:500; margin-left:8px; }}
  .train-close {{ border:none; background:#eef4fb; color:#41546e; width:34px; height:34px; border-radius:50%; cursor:pointer; font-size:16px; }}
  .train-body {{ padding:14px 22px; flex:1; }}
  .train-body h3 {{ margin:4px 0 8px; font-size:20px; color:#17293f; line-height:1.45; }}
  .train-body .t-sub {{ color:#6b7f95; font-size:13px; margin:0 0 10px; }}
  .train-body .t-tags {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:12px; }}
  .train-body .t-tags span {{ background:#f0f6ff; color:#3b6cb4; border-radius:999px; padding:3px 12px; font-size:12px; }}
  .train-body .t-badge {{ display:inline-block; font-size:12px; background:#f6f9fd; border:1px solid #e3edf7; border-radius:999px; padding:5px 12px; color:#51637a; }}
  .train-body .t-date {{ margin-left:8px; color:#8fa1b5; font-size:12px; }}
  .train-foot {{ display:flex; align-items:center; justify-content:space-between; gap:10px; padding:12px 22px 18px; flex-wrap:wrap; }}
  .train-nav {{ display:flex; gap:10px; align-items:center; }}
  .train-nav button {{
    border:1.5px solid #d6e4f2; background:#f8fbff; color:#1f2d3d; font-size:14px;
    padding:9px 18px; border-radius:12px; cursor:pointer; transition:all .15s;
  }}
  .train-nav button:disabled {{ opacity:.35; cursor:not-allowed; }}
  .train-nav button:not(:disabled):hover {{ border-color:#4f8ef7; color:#3b6cb4; }}
  .train-open {{
    border:none; cursor:pointer; font-size:14px; font-weight:600; color:#fff;
    background:linear-gradient(120deg,#4f8ef7,#22c3a6); padding:10px 22px; border-radius:12px; text-decoration:none;
  }}
  .train-opts {{ display:flex; gap:14px; align-items:center; font-size:13px; color:#51637a; flex-wrap:wrap; }}
  .train-opts label {{ display:flex; align-items:center; gap:5px; cursor:pointer; }}
  .train-opts select {{ border:1.5px solid #d6e4f2; border-radius:8px; padding:4px 6px; font-size:12px; background:#f8fbff; color:#1f2d3d; }}
  .train-redo input {{ transform:scale(1.15); cursor:pointer; }}
  .train-tip {{ font-size:11px; color:#9db0c4; padding:0 22px 14px; }}
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
  .cstat-line {{ margin-top:9px; }}
  .c-badge {{ display:inline-block; font-size:11px; padding:2px 9px; border-radius:999px; background:#f1f4f8; color:#7c8aa0; font-weight:600; }}
  .c-badge.st-forgot {{ background:#fee2e2; color:#dc2626; }}
  .c-badge.st-fuzzy {{ background:#fef3c7; color:#b45309; }}
  .c-badge.st-skilled {{ background:#ecfdf5; color:#059669; }}
  .forget-min {{ width:64px; padding:5px 6px; border:1px solid #d6e4f2; border-radius:8px; font-size:12.5px; font-family:inherit; }}
  .stat-meta {{ color:#93a7ba; }}
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
            <label class="popup-option dr-row"><span>\u4ece</span><input type="date" id="dateFrom" min="{dmin}" max="{dmax}"></label>
            <label class="popup-option dr-row"><span>\u81f3</span><input type="date" id="dateTo" min="{dmin}" max="{dmax}"></label>
          </div>
          <div class="popup-actions">
            <button type="button" id="dateClear">\u6e05\u9664</button>
            <button type="button" data-close="popupDate">\u786e\u5b9a</button>
          </div>
        </div>
      </div>
    </div>
    <div class="fld">
      <label>\u5b66\u4e60\u81ea\u8bc4</label>
      <div class="popup-filter">
        <button class="filter-btn" type="button" id="btnStatus">\u5b66\u4e60\u81ea\u8bc4 <span class="cnt zero" id="cntStatus">0</span></button>
        <div class="popup" id="popupStatus">
          <div class="popup-options">
            <label class="popup-option"><input type="checkbox" data-filter="status" value="new">⚪ \u672a\u8bad\u7ec3</label>
            <label class="popup-option"><input type="checkbox" data-filter="status" value="forgot">❌ \u9700\u91cd\u7ec3\uff08\u6709\u5fd8\u8bb0\uff09</label>
            <label class="popup-option"><input type="checkbox" data-filter="status" value="fuzzy">😐 \u5f85\u5de9\u56fa\uff08\u6709\u6a21\u7cca\uff09</label>
            <label class="popup-option"><input type="checkbox" data-filter="status" value="skilled">✅ \u5df2\u638c\u63e1\uff08\u5168\u719f\u7ec3\uff09</label>
          </div>
          <div class="popup-options drange">
            <label class="popup-option dr-row"><span>\u5fd8\u8bb0\u2265</span><input type="number" id="forgetMin" class="forget-min" min="1" placeholder="N"></label>
          </div>
          <div class="popup-actions">
            <button type="button" id="forgetMinClear">\u6e05\u9664\u9608\u503c</button>
            <button type="button" data-close="popupStatus">\u786e\u5b9a</button>
          </div>
        </div>
      </div>
    </div>
    <div class="fld">
      <label>\u8bfe\u4ef6\u8bc4\u4ef7</label>
      <div class="popup-filter">
        <button class="filter-btn" type="button" id="btnRating">\u8bfe\u4ef6\u8bc4\u4ef7 <span class="cnt zero" id="cntRating">0</span></button>
        <div class="popup" id="popupRating">
          <div class="popup-options">
            <label class="popup-option"><input type="checkbox" data-filter="rating" value="good">👍 \u597d</label>
            <label class="popup-option"><input type="checkbox" data-filter="rating" value="hard">📕 \u8bfe\u4ef6\u4e0d\u597d\u61c2</label>
            <label class="popup-option"><input type="checkbox" data-filter="rating" value="teach">🗣\ufe0f \u6ca1\u8001\u5e08\u8bb2\u7684\u597d</label>
          </div>
          <div class="popup-actions">
            <button type="button" data-clear="rating">\u6e05\u9664</button>
            <button type="button" data-close="popupRating">\u786e\u5b9a</button>
          </div>
        </div>
      </div>
    </div>
    <div class="fld">
      <label>\u72ec\u7acb\u91cd\u505a</label>
      <div class="popup-filter">
        <button class="filter-btn" type="button" id="btnRedo">\u72ec\u7acb\u91cd\u505a <span class="cnt zero" id="cntRedo">0</span></button>
        <div class="popup" id="popupRedo">
          <div class="popup-options">
            <label class="popup-option"><input type="checkbox" data-filter="redo" value="done">✍\ufe0f \u5df2\u72ec\u7acb\u91cd\u505a</label>
            <label class="popup-option"><input type="checkbox" data-filter="redo" value="undone">\u5c1a\u672a\u91cd\u505a</label>
          </div>
          <div class="popup-actions">
            <button type="button" data-clear="redo">\u6e05\u9664</button>
            <button type="button" data-close="popupRedo">\u786e\u5b9a</button>
          </div>
        </div>
      </div>
    </div>
    <div class="fld search">
      <label>\u641c\u7d22\u6807\u9898/\u6765\u6e90</label>
      <input id="fSearch" placeholder="\u8f93\u5165\u5173\u952e\u5b57\u2026" autocomplete="off">
    </div>
    <div class="fld">
      <label>\u6392\u5e8f</label>
      <select id="fSort" class="sort-select">
        <option value="visit-desc" selected>\u6d4f\u89c8\u65e5\u671f \u5012\u5e8f\uff08\u65b0\u2192\u65e7\uff09</option>
        <option value="visit-asc">\u6d4f\u89c8\u65e5\u671f \u6b63\u5e8f\uff08\u65e7\u2192\u65b0\uff09</option>
        <option value="forgot-desc">\u5fd8\u8bb0\u6570 \u5012\u5e8f\uff08\u91cd\u7ec3\u4f18\u5148\uff09</option>
        <option value="date-desc">\u65e5\u671f \u5012\u5e8f\uff08\u65b0\u2192\u65e7\uff09</option>
        <option value="date-asc">\u65e5\u671f \u6b63\u5e8f\uff08\u65e7\u2192\u65b0\uff09</option>
        <option value="num-desc">\u7f16\u53f7 \u5012\u5e8f\uff08\u65b0\u2192\u65e7\uff09</option>
        <option value="num-asc">\u7f16\u53f7 \u6b63\u5e8f\uff08\u65e7\u2192\u65b0\uff09</option>
      </select>
    </div>
    <button class="reset-btn" id="statRefresh" type="button" title="\u4ece\u4e91\u7aef\u91cd\u65b0\u62c9\u53d6\u7edf\u8ba1">🔄 \u5237\u65b0\u7edf\u8ba1</button>
    <button class="reset-btn" id="fReset" type="button">\u91cd\u7f6e</button>
  </div>
  <div class="active-filters" id="activeFilters"></div>
  <div class="result-info" id="resultInfo">\u5171 <span id="resultCount">{count}</span> \u4e2a\u8bfe\u4ef6 <span class="stat-meta" id="statMeta"></span><button class="train-btn" id="trainBtn" type="button" title="\u5c06\u5f53\u524d\u7b5b\u9009\u7ed3\u679c\u4f5c\u4e3a\u4e00\u7ec4\u9898\uff0c\u9010\u5f20\u6d4f\u89c8\u8bad\u7ec3">🎯 \u4e13\u9898\u7ec3</button></div>

  <div class="grid" id="grid">
{cards}
  </div>
  <!-- 专题练训练面板 -->
  <div id="trainOverlay">
    <div class="train-panel">
      <div class="train-head">
        <div class="train-progress"><span id="trainProgress">1 / 1</span><small id="trainOrderLbl">顺序</small></div>
        <button class="train-close" id="trainClose" type="button" title="\u9000\u51fa (Esc)">✕</button>
      </div>
      <div class="train-body">
        <h3 id="trainTitle"></h3>
        <p class="t-sub" id="trainSub"></p>
        <div class="t-tags" id="trainTags"></div>
        <div><span class="t-badge" id="trainBadge"></span><span class="t-date" id="trainDate"></span></div>
      </div>
      <div class="train-foot">
        <div class="train-nav">
          <button id="trainPrev" type="button" title="\u5feb\u6377\u952e \u2190">← \u4e0a\u4e00\u9898</button>
          <button id="trainNext" type="button" title="\u5feb\u6377\u952e \u2192">\u4e0b\u4e00\u9898 →</button>
        </div>
        <a class="train-open" id="trainOpen" href="#" target="_blank" rel="noopener">\u6253\u5f00\u8bfe\u4ef6 \u2197</a>
        <div class="train-opts">
          <label>\u987a\u5e8f
            <select id="trainOrder">
              <option value="seq" selected>\u987a\u5e8f</option>
              <option value="random">\u968f\u673a</option>
            </select>
          </label>
          <label class="train-redo"><input type="checkbox" id="trainRedo">✍️ \u5df2\u72ec\u7acb\u91cd\u505a</label>
        </div>
      </div>
      <div class="train-tip">\u5feb\u6377\u952e：← \u4e0a\u4e00\u9898 · → \u4e0b\u4e00\u9898 · Esc \u9000\u51fa；\u4e0a\u6b21\u7ec3\u5230\u7684\u4f4d\u7f6e\u4f1a\u81ea\u52a8\u8bb0\u5fc6</div>
    </div>
  </div>
  <div class="foot"><a href="manage.html">\u6807\u7b7e\u7ba1\u7406</a> \u00b7 mcjc4 \u00b7 GitHub Pages \u00b7 \u9875\u9762\u751f\u6210\u4e8e {date}</div>
</div>
<script>
(function(){{
  var grid=document.getElementById('grid');
  var cards=Array.from(grid.querySelectorAll('.card'));
  var fQ=document.getElementById('fSearch');
  var info=document.getElementById('resultInfo');
  var sets={{subject:new Set(),chapter:new Set(),knowledge:new Set(),method:new Set(),date:new Set(),status:new Set(),rating:new Set(),redo:new Set()}};
  var cntIds={{subject:'cntSubject',chapter:'cntChapter',knowledge:'cntKnowledge',method:'cntMethod',date:'cntDate',status:'cntStatus',rating:'cntRating',redo:'cntRedo'}};
  var dateFrom=document.getElementById('dateFrom');
  var dateTo=document.getElementById('dateTo');
  var fSort=document.getElementById('fSort');
  var forgetMin=document.getElementById('forgetMin');

  function sortCards(){{
    var mode=fSort.value||'visit-desc';
    var desc=mode.indexOf('-desc')>0;
    // 浏览日期排序：主键=毫秒级真实浏览时间戳（刚浏览的必排最前），无浏览记录的按制作日期兜底、再按编号
    function visitKey(card){{
      var ts=+card.dataset.browseTs||0;
      if(ts>0) return [2,ts,0];
      var d=card.dataset.date||'';
      return [1,(new Date(d).getTime()||0),(+card.dataset.num||0)];
    }}
    var keyOf=function(card){{
      if(mode.indexOf('forgot')===0) return (+card.dataset.forgot||0);
      if(mode.indexOf('visit')===0) return visitKey(card);
      if(mode.indexOf('date')===0) return card.dataset.date||'';
      return (+card.dataset.num||0);
    }};
    var numeric=(mode.indexOf('forgot')===0||mode.indexOf('num')===0);
    var sorted=cards.slice().sort(function(a,b){{
      var ka=keyOf(a),kb=keyOf(b);
      var r;
      if(mode.indexOf('visit')===0){{
        // 数组逐位比较
        for(var i=0;i<3;i++){{ if(ka[i]!==kb[i]){{ r=ka[i]<kb[i]?-1:1; return desc?-r:r; }} }}
        r=0;
      }}else{{
        r=numeric?(ka-kb):(ka<kb?-1:(ka>kb?1:0));
      }}
      return desc?-r:r;
    }});
    sorted.forEach(function(c){{grid.appendChild(c);}});
  }}

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

  var currentQ='';
  var FNAME={{subject:'学科',chapter:'章节',knowledge:'知识点',method:'解法',status:'学习自评',rating:'课件评价',redo:'独立重做'}};
  var RLBL={{good:'好',hard:'课件不好懂',teach:'没老师讲的好'}};
  var SLBL={{new:'未训练',forgot:'需重练',fuzzy:'待巩固',skilled:'已掌握'}};
  function syncChecks(f,v){{
    document.querySelectorAll('.popup-option input[data-filter="'+f+'"]').forEach(function(cb){{if(cb.value===v)cb.checked=false;}});
  }}
  function renderChips(){{
    var box=document.getElementById('activeFilters');
    var chips=[];
    ['subject','chapter','knowledge','method','status','rating','redo'].forEach(function(f){{
      sets[f].forEach(function(v){{
        var shown=(f==='status')?(SLBL[v]||v):((f==='rating')?(RLBL[v]||v):v);
        chips.push({{label:FNAME[f]+'：'+shown, del:function(){{sets[f].delete(v);syncChecks(f,v);updateCnt(f);apply();}}}});
      }});
    }});
    var fm=parseInt(forgetMin.value,10)||0;
    if(fm>0){{
      chips.push({{label:'忘记≥'+fm, del:function(){{forgetMin.value='';apply();}}}});
    }}
    if(dateFrom.value||dateTo.value){{
      chips.push({{label:'浏览：'+(dateFrom.value||'早期')+' ~ '+(dateTo.value||'今天'), del:function(){{dateFrom.value='';dateTo.value='';updateDateCnt();apply();}}}});
    }}
    if(currentQ){{
      chips.push({{label:'搜索：'+currentQ, del:function(){{fQ.value='';currentQ='';apply();}}}});
    }}
    if(!chips.length){{box.innerHTML='';return;}}
    var out=['<span class="af-label">筛选条件：</span>'];
    chips.forEach(function(c,i){{
      out.push('<span class="af-chip" data-ci="'+i+'">'+c.label+'<span class="x" title="删除此条件"></span></span>');
    }});
    box.innerHTML=out.join('');
    box.querySelectorAll('.af-chip').forEach(function(el){{
      el.querySelector('.x').addEventListener('click',function(){{chips[+el.getAttribute('data-ci')].del();}});
    }});
  }}

  function apply(){{
    sortCards();
    var q=fQ.value.trim().toLowerCase();
    currentQ=fQ.value.trim();
    var fm=parseInt(forgetMin.value,10)||0;
    var n=0;
    cards.forEach(function(card){{
      var okS=sets.subject.size===0||sets.subject.has(card.dataset.subject);
      var okC=sets.chapter.size===0||sets.chapter.has(card.dataset.chapter);
      var okK=sets.knowledge.size===0||sets.knowledge.has(card.dataset.knowledge);
      var okM=sets.method.size===0||sets.method.has(card.dataset.method);
      var okSt=sets.status.size===0||sets.status.has(card.dataset.status);
      var cr=(card.dataset.rating||'').split(',');
      var okRt=sets.rating.size===0||cr.some(function(v){{return v&&sets.rating.has(v);}});
      var rd=card.dataset.redo==='1';
      var okRd=sets.redo.size===0||(sets.redo.has('done')&&rd)||(sets.redo.has('undone')&&!rd);
      var okFm=!fm||(+card.dataset.forgot||0)>=fm;
      var dv=card.dataset.browse||card.dataset.date||'';
      var okD=(!dateFrom.value||dv>=dateFrom.value)&&(!dateTo.value||dv<=dateTo.value);
      var okQ=!q||(card.textContent||'').toLowerCase().indexOf(q)>=0;
      var show=okS&&okC&&okK&&okM&&okSt&&okRt&&okRd&&okFm&&okD&&okQ;
      card.style.display=show?'':'none';
      if(show)n++;
    }});
    var rc=document.getElementById('resultCount');
    if(rc)rc.textContent=n; // 只更新数字；不能用 textContent 覆盖整个 resultInfo（会清掉 statMeta 子节点）
    var tb=document.getElementById('trainBtn');
    if(tb)tb.style.display=n>0?'':'none'; // 无筛选结果时隐藏专题练入口
    var empty=document.getElementById('emptyHint');
    if(n===0){{
      if(!empty){{empty=document.createElement('div');empty.className='empty';empty.id='emptyHint';empty.textContent='\u6ca1\u6709\u7b26\u5408\u6761\u4ef6\u7684\u8bfe\u4ef6\uff0c\u8bd5\u8bd5\u6362\u4e2a\u7b5b\u9009\u6761\u4ef6\u3002';grid.appendChild(empty);}}
    }}else{{if(empty)empty.remove();}}
    renderChips();
    // 持久化筛选状态：从课件返回导航页时恢复（陈总需求）
    try{{
      localStorage.setItem('nav_filters',JSON.stringify({{
        sets:{{subject:Array.from(sets.subject),chapter:Array.from(sets.chapter),knowledge:Array.from(sets.knowledge),method:Array.from(sets.method),status:Array.from(sets.status),rating:Array.from(sets.rating),redo:Array.from(sets.redo)}},
        df:dateFrom.value,dt:dateTo.value,fm:forgetMin.value,q:currentQ,sort:fSort.value}}));
    }}catch(e){{}}
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
  fSort.addEventListener('change',apply);
  forgetMin.addEventListener('input',apply);
  document.getElementById('forgetMinClear').addEventListener('click',function(){{
    forgetMin.value='';apply();
  }});
  document.getElementById('fReset').addEventListener('click',function(){{
    ['subject','chapter','knowledge','method','date','status','rating','redo'].forEach(function(f){{
      sets[f].clear();
      document.querySelectorAll('.popup-option input[data-filter="'+f+'"]').forEach(function(cb){{cb.checked=false;}});
      updateCnt(f);
    }});
    dateFrom.value='';dateTo.value='';updateDateCnt();
    forgetMin.value='';
    fQ.value='';apply();
  }});

  // 恢复上次筛选状态：从课件页返回导航页时筛选结果不丢（须在首次 apply 前执行）
  (function(){{
    var sv=null; try{{ sv=JSON.parse(localStorage.getItem('nav_filters')); }}catch(e){{}}
    if(sv&&sv.sets){{
      ['subject','chapter','knowledge','method','status','rating','redo'].forEach(function(f){{
        (sv.sets[f]||[]).forEach(function(v){{
          sets[f].add(v);
          document.querySelectorAll('.popup-option input[data-filter="'+f+'"]').forEach(function(cb){{if(cb.value===v)cb.checked=true;}});
        }});
        updateCnt(f);
      }});
    }}
    if(sv){{
      if(sv.df)dateFrom.value=sv.df;
      if(sv.dt)dateTo.value=sv.dt;
      updateDateCnt();
      if(sv.fm)forgetMin.value=sv.fm;
      if(sv.q)fQ.value=sv.q;
      if(sv.sort)fSort.value=sv.sort;
    }}
  }})();

  __STATS_JS__
  sortCards();
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


# 统计联动 JS（经 .replace 注入 IIFE 内，花括号无需双写）
STATS_JS = r"""
/* ===== 统计联动：本机直读 + 云端 max 合并 + 徽章（SOP §3.2~3.4）===== */
var COURSES = __COURSES_JSON__;
var cardByCid={};
cards.forEach(function(card){ var cid=card.dataset.cid; if(cid)cardByCid[cid]=card; });
var STAT_CACHE='nav_course_stats_cache';
var statMap={};
function statusOf(s){
  if(!s||(s.skilled+s.fuzzy+s.forgot)===0) return 'new';
  if(s.forgot>0) return 'forgot';
  if(s.fuzzy>0) return 'fuzzy';
  return 'skilled';
}
function fmtTs(ts){ if(!ts)return ''; var d=new Date(ts); return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2); }
function collectLocal(){
  var out={};
  COURSES.forEach(function(c){
    var s={}; try{ s=JSON.parse(localStorage.getItem('cstat:'+c.id))||{}; }catch(e){}
    var r={}; try{ r=JSON.parse(localStorage.getItem('crate:'+c.id))||{}; }catch(e){}
    var d={}; try{ d=JSON.parse(localStorage.getItem('credo:'+c.id))||{}; }catch(e){}
    var lv=0; try{ var v=JSON.parse(localStorage.getItem('cvisit:'+c.id)); if(v&&v.ts)lv=v.ts; }catch(e){}
    out[c.id]={skilled:s.skilled||0,fuzzy:s.fuzzy||0,forgot:s.forgot||0,
               rg:r.good||0,rh:r.hard||0,rt:r.teach||0,
               rd:d.done===1,rts:d.ts||0,
               visit:lv,ts:s.ts||0};
  });
  return out;
}
// 清零感知合并：熟练清零后 fuzzy/forgot 变小，max 会复活旧值 → 新 ts 侧为 0 时取 0（清零生效），否则 max
function mergeStats(loc,cl){
  var lts=loc.ts||0,cts=cl.ts||0;
  function cnt(lv,cvv){
    lv=lv||0;cvv=cvv||0;
    if(lts>cts&&lv===0&&cvv>0)return 0;
    if(cts>lts&&cvv===0&&lv>0)return 0;
    return Math.max(lv,cvv);
  }
  return {
    skilled:Math.max(loc.skilled||0,cl.skilled||0),
    fuzzy:cnt(loc.fuzzy,cl.fuzzy),
    forgot:cnt(loc.forgot,cl.forgot),
    // 独立重做是状态不是累计：按重做自身 ts（rts）与云端 updated_at 较新侧为准
    // （不能用自评 cstat 的 ts——从未打开过的课件 ts=0，导航页勾的重做会被云端顶掉）
    rd:(loc.rts&&loc.rts>cts)?!!loc.rd:!!cl.rd
  };
}
function ratingStr(s){
  var p=[];
  if(s.rg)p.push('👍'+s.rg);
  if(s.rh)p.push('📕'+s.rh);
  if(s.rt)p.push('🗣️'+s.rt);
  return p.length?(' · ⭐'+p.join(' ')):'';
}
function renderBadge(cv){
  var card=cardByCid[cv.id]; if(!card)return;
  var el=card.querySelector('.c-badge'); if(!el)return;
  var s=cv.stats, st=cv.status;
  card.dataset.status=st;
  card.dataset.forgot=s.forgot||0;
  var rk=[];
  if(s.rg)rk.push('good'); if(s.rh)rk.push('hard'); if(s.rt)rk.push('teach');
  card.dataset.rating=rk.join(',');
  card.dataset.redo=s.rd?'1':'0';
  card.dataset.browse=cv.visitTs?fmtTs(cv.visitTs):(card.dataset.date||'');
  card.dataset.browseTs=String(cv.visitReal||0); // 毫秒级真实浏览时间戳（无浏览=0），排序用
  var when=cv.visitTs?fmtTs(cv.visitTs):(card.dataset.date||'—');
  var rt=ratingStr(s)+(s.rd?' · ✍️已重做':'');
  if(st==='new'){ el.textContent='⚪ 未训练 · 🕓 '+when+rt; el.className='c-badge st-new'; }
  else if(st==='forgot'){ el.textContent='❌ 需重练 · ✅'+s.skilled+' 😐'+s.fuzzy+' ❌'+s.forgot+' · 🕓 '+when+rt; el.className='c-badge st-forgot'; }
  else if(st==='fuzzy'){ el.textContent='😐 待巩固 · ✅'+s.skilled+' 😐'+s.fuzzy+' ❌'+s.forgot+' · 🕓 '+when+rt; el.className='c-badge st-fuzzy'; }
  else { el.textContent='✅ 已掌握 · ✅'+s.skilled+' 😐'+s.fuzzy+' ❌'+s.forgot+' · 🕓 '+when+rt; el.className='c-badge st-skilled'; }
}
function applyStats(map){
  statMap=map||{};
  var local=collectLocal();
  COURSES.forEach(function(cv){
    var loc=local[cv.id]||{};
    var cl=statMap[cv.id]||{};
    // 熟练清零感知合并（fuzzy/forgot 新侧为 0 取 0），skilled 只增不减
    cv.stats=mergeStats(loc,cl);
    // 评价：累计计数只增不减，max 合并
    cv.stats.rg=Math.max(loc.rg||0,cl.rg||0);
    cv.stats.rh=Math.max(loc.rh||0,cl.rh||0);
    cv.stats.rt=Math.max(loc.rt||0,cl.rt||0);
    // 浏览时间：本机与云端取最大，为空回退制作日期
    cv.visitReal=Math.max(loc.visit||0,cl.visit||0)||0;
    cv.visitTs=cv.visitReal||((cv.date&&(new Date(cv.date).getTime()))||0);
    cv.status=statusOf(cv.stats);
    renderBadge(cv);
  });
  apply(); // apply 内含 sortCards，云端回来后顺序自动刷新（SOP §3.6）
}
function fetchCloud(isRetry){
  var cfg={url:'https://mixuqjognbdrafrrlivc.supabase.co',key:'sb_publishable_D0ha7g4X4LutG-3hxCguSA_pwyQLrVX'};
  try{ var c=JSON.parse(localStorage.getItem('course_cloud_cfg')); if(c&&c.url&&c.key)cfg=c; }catch(e){}
  var ctl=('AbortController' in window)?new AbortController():null;
  var timer=ctl?setTimeout(function(){ try{ctl.abort();}catch(e){} },15000):null; // 15s！
  var meta=document.getElementById('statMeta');
  fetch(cfg.url.replace(/\/+$/,'')+'/rest/v1/course_stats?select=*',{
    headers:{'apikey':cfg.key,'Authorization':'Bearer '+cfg.key},
    signal:ctl?ctl.signal:undefined
  })
  .then(function(r){ if(!r.ok)throw new Error('http '+r.status); return r.json(); })
  .then(function(rows){
    var map={};
    (rows||[]).forEach(function(r){
      map[r.course_id]={skilled:r.skilled||0,fuzzy:r.fuzzy||0,forgot:r.forgot||0,
                        rg:r.rating_good||0,rh:r.rating_hard||0,rt:r.rating_teach||0,
                        rd:r.redone===true,
                        visit:r.last_visit?new Date(r.last_visit).getTime():0,
                        ts:r.updated_at?new Date(r.updated_at).getTime():0};
    });
    applyStats(map);
    try{ localStorage.setItem(STAT_CACHE,JSON.stringify({ts:Date.now(),rows:map})); }catch(e){}
    if(meta)meta.textContent='· 云端 '+Object.keys(map).length+' 张已上报 '+fmtTs(Date.now());
  })
  .catch(function(){
    if(!isRetry){ if(meta)meta.textContent='· 云端拉取中…'; setTimeout(function(){ fetchCloud(true); },2500); return; }
    if(meta)meta.textContent='· 云端暂不可达，显示本机/缓存数据';
    var c=null; try{ c=JSON.parse(localStorage.getItem(STAT_CACHE)); }catch(e){}
    if(c&&c.rows)applyStats(c.rows); else applyStats(collectLocal());
  })
  .then(function(){ if(timer)clearTimeout(timer); });
}
// 首屏：缓存秒显 → 云端合并
var cached0=null; try{ cached0=JSON.parse(localStorage.getItem(STAT_CACHE)); }catch(e){}
applyStats(cached0&&cached0.rows?cached0.rows:collectLocal());
fetchCloud();
document.getElementById('statRefresh').addEventListener('click',function(){
  var meta=document.getElementById('statMeta');
  if(meta)meta.textContent='· 刷新中…';
  fetchCloud();
});

/* ===== 专题练：筛选结果逐张浏览训练 ===== */
var trainOv=document.getElementById('trainOverlay');
var trainList=[], trainIdx=0;
var trainBtn=document.getElementById('trainBtn');
var orderSel=document.getElementById('trainOrder');
try{ var to=localStorage.getItem('train_order'); if(to)orderSel.value=to; }catch(e){}
document.getElementById('trainOrderLbl').textContent=(orderSel.value==='random')?'随机':'顺序';

var cfgT={url:'https://mixuqjognbdrafrrlivc.supabase.co',key:'sb_publishable_D0ha7g4X4LutG-3hxCguSA_pwyQLrVX'};
try{ var ccfg=JSON.parse(localStorage.getItem('course_cloud_cfg')); if(ccfg&&ccfg.url&&ccfg.key)cfgT=ccfg; }catch(e){}

function visibleCards(){ return cards.filter(function(c){ return c.style.display!=='none'; }); }
function shuffleArr(arr){
  var a=arr.slice();
  for(var i=a.length-1;i>0;i--){ var j=Math.floor(Math.random()*(i+1)); var t=a[i];a[i]=a[j];a[j]=t; }
  return a;
}
function trainRender(){
  var card=trainList[trainIdx]; if(!card)return;
  var cid=card.dataset.cid||'';
  document.getElementById('trainProgress').textContent=(trainIdx+1)+' / '+trainList.length;
  var h=card.querySelector('h3');
  document.getElementById('trainTitle').textContent=h?h.textContent:'';
  var sub=card.querySelector('.sub');
  document.getElementById('trainSub').textContent=sub?sub.textContent:'';
  var tags=card.querySelector('.tags');
  document.getElementById('trainTags').innerHTML=tags?tags.innerHTML:'';
  var badge=card.querySelector('.c-badge');
  var be=document.getElementById('trainBadge');
  be.textContent=badge?badge.textContent:'';
  be.className='t-badge '+(badge&&badge.className.split(' ')[1]||'');
  document.getElementById('trainDate').textContent='制作 '+(card.dataset.date||'—');
  document.getElementById('trainOpen').setAttribute('href',card.getAttribute('href')+'?tr='+trainIdx); // 带序号，课件页显示串联导航
  var rd=document.getElementById('trainRedo');
  var d={}; try{ d=JSON.parse(localStorage.getItem('credo:'+cid))||{}; }catch(e){}
  rd.checked=d.done===1;
  rd.dataset.cid=cid;
  document.getElementById('trainPrev').disabled=(trainIdx<=0);
  document.getElementById('trainNext').disabled=(trainIdx>=trainList.length-1);
  try{ localStorage.setItem('train_pos',JSON.stringify({n:trainList.length,i:trainIdx})); }catch(e){}
}
function trainOpenPanel(){
  var vis=visibleCards();
  if(!vis.length)return;
  trainList=(orderSel.value==='random')?shuffleArr(vis):vis.slice();
  trainIdx=0;
  try{ // 位置记忆：题目数一致时恢复上次练到的位置
    var p=JSON.parse(localStorage.getItem('train_pos'));
    if(p&&p.n===trainList.length&&p.i>=0&&p.i<trainList.length)trainIdx=p.i;
  }catch(e){}
  trainOv.classList.add('open');
  try{ localStorage.setItem('train_group',JSON.stringify({urls:trainList.map(function(c){return c.getAttribute('href');}),ts:Date.now()})); }catch(e){}
  trainRender();
}
function trainClosePanel(){ trainOv.classList.remove('open'); }
function trainStep(d){
  var ni=trainIdx+d;
  if(ni<0||ni>=trainList.length)return;
  trainIdx=ni; trainRender();
}
// 面板内勾「已独立重做」→ 本机 + 徽章 + 云端合并上报
function syncRedo(cid,done){
  var h={'apikey':cfgT.key,'Authorization':'Bearer '+cfgT.key,'Content-Type':'application/json'};
  var base=cfgT.url.replace(/\/+$/,'')+'/rest/v1/course_stats';
  fetch(base+'?course_id=eq.'+encodeURIComponent(cid),{headers:h})
  .then(function(r){ return r.ok?r.json():[]; })
  .then(function(rows){
    var row=(rows&&rows[0])||{};
    var cl={skilled:row.skilled||0,fuzzy:row.fuzzy||0,forgot:row.forgot||0,
            rg:row.rating_good||0,rh:row.rating_hard||0,rt:row.rating_teach||0,
            rd:row.redone===true,
            visit:row.last_visit?new Date(row.last_visit).getTime():0,
            ts:row.updated_at?new Date(row.updated_at).getTime():0};
    var loc=collectLocal()[cid]||{};
    var m=mergeStats(loc,cl);
    m.rg=Math.max(loc.rg||0,cl.rg||0);
    m.rh=Math.max(loc.rh||0,cl.rh||0);
    m.rt=Math.max(loc.rt||0,cl.rt||0);
    var body={course_id:cid,skilled:m.skilled,fuzzy:m.fuzzy,forgot:m.forgot,
              rating_good:m.rg,rating_hard:m.rh,rating_teach:m.rt,
              redone:!!done,updated_at:new Date().toISOString(),
              last_visit:loc.visit?new Date(loc.visit).toISOString():null};
    return fetch(base+'?on_conflict=course_id',{
      method:'POST',headers:Object.assign({'Prefer':'resolution=merge-duplicates'},h),
      body:JSON.stringify(body)});
  }).catch(function(){ /* 云端不可达不阻塞，本机已记账 */ });
}
trainBtn.addEventListener('click',trainOpenPanel);
document.getElementById('trainClose').addEventListener('click',trainClosePanel);
document.getElementById('trainPrev').addEventListener('click',function(){trainStep(-1);});
document.getElementById('trainNext').addEventListener('click',function(){trainStep(1);});
orderSel.addEventListener('change',function(){
  try{ localStorage.setItem('train_order',orderSel.value); }catch(e){}
  document.getElementById('trainOrderLbl').textContent=(orderSel.value==='random')?'随机':'顺序';
  var cur=trainList[trainIdx];
  var vis=visibleCards();
  trainList=(orderSel.value==='random')?shuffleArr(vis):vis.slice();
  trainIdx=0;
  if(cur){ var k=trainList.indexOf(cur); if(k>=0)trainIdx=k; }
  try{ localStorage.setItem('train_group',JSON.stringify({urls:trainList.map(function(c){return c.getAttribute('href');}),ts:Date.now()})); }catch(e){}
  trainRender();
});
document.getElementById('trainRedo').addEventListener('change',function(){
  var cid=this.dataset.cid; if(!cid)return;
  try{ localStorage.setItem('credo:'+cid,JSON.stringify({done:this.checked?1:0,ts:Date.now()})); }catch(e){}
  applyStats(statMap); // 立即刷新卡片徽章与 data-redo
  syncRedo(cid,this.checked);
});
document.addEventListener('keydown',function(e){
  if(!trainOv.classList.contains('open'))return;
  if(e.key==='ArrowLeft'){trainStep(-1);}
  else if(e.key==='ArrowRight'){trainStep(1);}
  else if(e.key==='Escape'){trainClosePanel();}
});
"""


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
            num_attr=html.escape(str(it['order'])),
            cid=html.escape(it['cid']),
            sub=html.escape(it['sub']), tags=tags, source_html=source_html,
            subject=html.escape(it['subject']), chapter=html.escape(it['chapter']),
            knowledge=html.escape(it['knowledge']),
            method=html.escape(it['method']), date=html.escape(it['date']),
            tags_attr=html.escape(';'.join(it.get('tags_list', []))),
        ))
    cards_html = '\n'.join(cards) if cards else '    <div class="empty">暂无课件</div>'

    today = datetime.now().strftime('%Y-%m-%d')
    courses_json = json.dumps([{
        'id': it['cid'],
        'title': it['title'],
        'subject': it['subject'],
        'chapter': it['chapter'],
        'points': it['points'],
        'date': it['date'],
    } for it in items], ensure_ascii=False, separators=(',', ':'))
    page = PAGE_TMPL.format(
        count=len(items), subject_count=len(subjects), chapter_count=len(chapters),
        tag_count=len(all_tags),
        subject_checks=check_opts(subjects, 'subject'),
        chapter_checks=check_opts(chapters, 'chapter'),
        knowledge_checks=check_opts(knowledges, 'knowledge'),
        method_checks=check_opts(methods, 'method'),
        dmin=dates_asc[0] if dates_asc else '2026-01-01',
        dmax=datetime.now().strftime('%Y-%m-%d'),
        cards=cards_html, date=today,
    )
    page = page.replace('__STATS_JS__', STATS_JS).replace('__COURSES_JSON__', courses_json)
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