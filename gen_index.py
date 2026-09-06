#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
courseware-site 导航首页生成器（带学科/章节/知识点筛选）
用法：在 courseware-site 根目录运行  python gen_index.py
约定：每课一个目录 lessons/<序号>-<英文短名>/index.html
      <title> 建议格式「主标题 · 副标题」（无「·」则整体作为标题）
      推荐在 <head> 中加 meta 标签：
        <meta name="subject" content="数学">
        <meta name="chapter" content="三角函数">
        <meta name="knowledge" content="半角公式">
        <meta name="source" content="2023·新高考全国II">
        <meta name="type" content="单选题">
产出：根目录 index.html（Fresh Gradient 教育风课件导航页，支持筛选）
"""
import os, re, glob, html, json
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
LESSONS_DIR = os.path.join(ROOT, 'lessons')
OUT = os.path.join(ROOT, 'index.html')


def extract_meta(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            head = f.read(200000)
    except Exception:
        return {'title': '未命名课件', 'sub': '', 'subject': '', 'chapter': '',
                'knowledge': '', 'source': '', 'type': ''}
    info = {'title': '未命名课件', 'sub': '', 'subject': '', 'chapter': '',
            'knowledge': '', 'source': '', 'type': ''}
    m = re.search(r'<title[^>]*>(.*?)</title>', head, re.S | re.I)
    if m:
        t = html.unescape(re.sub(r'\s+', ' ', m.group(1))).strip()
        if '·' in t:
            main, _, sub = t.partition('·')
            info['title'], info['sub'] = main.strip(), sub.strip()
        else:
            info['title'] = t
    for key in ('subject', 'chapter', 'knowledge', 'source', 'type'):
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
        items.append({
            'order': order,
            'num': num.group(1).zfill(2) if num else '',
            'link': 'lessons/' + name + '/',
            'title': meta['title'],
            'sub': meta['sub'] or '互动解题课件',
            'date': mtime,
            'subject': meta['subject'] or '未分类',
            'chapter': meta['chapter'] or '未分类',
            'knowledge': meta['knowledge'] or '未分类',
            'source': meta['source'] or '',
            'type': meta['type'] or '',
        })
    items.sort(key=lambda x: x['order'])
    for i, it in enumerate(items, 1):
        if not it['num']:
            it['num'] = str(i).zfill(2)
    return items


CARD_TMPL = """    <a class="card" href="{link}" target="_blank" rel="noopener" data-subject="{subject}" data-chapter="{chapter}" data-knowledge="{knowledge}">
      <span class="badge">{num}</span>
      <div class="card-body">
        <h3>{title}</h3>
        <p class="sub">{sub}</p>
        <div class="tags">{tags}</div>
        {source_html}
        <span class="go">打开课件 →</span>
      </div>
    </a>"""

PAGE_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>高考解题课件库 · 互动课件导航</title>
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
  .fld {{ display:flex; flex-direction:column; gap:5px; flex:1 1 180px; }}
  .fld label {{ font-size:12px; color:#5c7185; font-weight:600; }}
  .fld select, .fld input {{
    padding:9px 12px; border:1.5px solid #d6e4f2; border-radius:10px; font-size:14px;
    background:#f8fbff; color:#1f2d3d; font-family:inherit;
  }}
  .fld select:focus, .fld input:focus {{ outline:none; border-color:#4f8ef7; }}
  .fld.search {{ flex:2 1 240px; }}
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
    flex:none; width:40px; height:40px; border-radius:50%;
    background:linear-gradient(135deg,#4f8ef7,#22c3a6); color:#fff;
    display:flex; align-items:center; justify-content:center;
    font-size:14px; font-weight:600;
  }}
  .card-body {{ min-width:0; flex:1; }}
  .card-body h3 {{ font-size:16px; color:#1f2d3d; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
  .card-body .sub {{ font-size:13px; color:#5c7185; margin-top:5px; line-height:1.5; }}
  .tags {{ display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }}
  .tag-chip {{
    font-size:11px; padding:2px 9px; border-radius:999px; background:#eef3ff; color:#2a6df4;
  }}
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
</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <span class="tag">互动解题课件库 · 单文件离线可用</span>
    <h1>高考解题课件库</h1>
    <p>Fresh Gradient 教育风互动课件：逐步推导、即时反馈、KaTeX 公式渲染，全部内嵌单文件，可离线打开。支持按<b>学科 / 章节 / 知识点</b>筛选。</p>
    <div class="stat">
      <div><b>{count}</b><span>个课件</span></div>
      <div><b>{subject_count}</b><span>个学科</span></div>
      <div><b>{chapter_count}</b><span>个章节</span></div>
      <div><b>单文件</b><span>零依赖离线运行</span></div>
    </div>
  </div>

  <div class="filters">
    <div class="fld">
      <label>学科</label>
      <select id="fSubject"><option value="">全部</option>{subject_options}</select>
    </div>
    <div class="fld">
      <label>所属章节</label>
      <select id="fChapter"><option value="">全部</option>{chapter_options}</select>
    </div>
    <div class="fld">
      <label>知识点</label>
      <select id="fKnowledge"><option value="">全部</option>{knowledge_options}</select>
    </div>
    <div class="fld search">
      <label>搜索标题/来源</label>
      <input id="fSearch" placeholder="输入关键字…" />
    </div>
    <button class="reset-btn" id="fReset">重置</button>
  </div>
  <div class="result-info" id="resultInfo">共 {count} 个课件</div>

  <div class="grid" id="grid">
{cards}
  </div>
  <div class="foot">mcjc4 · GitHub Pages · 页面生成于 {date}</div>
</div>
<script>
(function(){{
  const grid=document.getElementById('grid');
  const cards=Array.from(grid.querySelectorAll('.card'));
  const fS=document.getElementById('fSubject');
  const fC=document.getElementById('fChapter');
  const fK=document.getElementById('fKnowledge');
  const fQ=document.getElementById('fSearch');
  const info=document.getElementById('resultInfo');
  function apply(){{
    const s=fS.value,c=fC.value,k=fK.value,q=fQ.value.trim().toLowerCase();
    let n=0;
    cards.forEach(card=>{{
      const okS=!s||card.dataset.subject===s;
      const okC=!c||card.dataset.chapter===c;
      const okK=!k||card.dataset.knowledge===k;
      const okQ=!q||(card.textContent||'').toLowerCase().includes(q);
      const show=okS&&okC&&okK&&okQ;
      card.style.display=show?'':'none';
      if(show) n++;
    }});
    info.textContent='共 '+n+' 个课件';
    if(n===0){{
      if(!document.getElementById('empty')){{
        const e=document.createElement('div');e.className='empty';e.id='empty';
        e.textContent='没有符合条件的课件，试试换个筛选条件。';
        grid.appendChild(e);
      }}
    }}else{{
      const e=document.getElementById('empty'); if(e) e.remove();
    }}
  }}
  [fS,fC,fK,fQ].forEach(el=>el.addEventListener('input',apply));
  document.getElementById('fReset').onclick=()=>{{fS.value='';fC.value='';fK.value='';fQ.value='';apply();}};
}})();
</script>
</body>
</html>"""


def main():
    items = scan_lessons()
    subjects = sorted({it['subject'] for it in items if it['subject']})
    chapters = sorted({it['chapter'] for it in items if it['chapter']})
    knowledges = sorted({it['knowledge'] for it in items if it['knowledge']})

    def opts(values):
        return ''.join(f'<option value="{html.escape(v)}">{html.escape(v)}</option>' for v in values)

    cards = []
    for it in items:
        tags = (f'<span class="tag-chip">{html.escape(it["subject"])}</span>'
                f'<span class="tag-chip c">{html.escape(it["chapter"])}</span>'
                f'<span class="tag-chip k">{html.escape(it["knowledge"])}</span>')
        if it['type']:
            tags += f'<span class="tag-chip" style="background:#f3e8ff;color:#8b5cf6">{html.escape(it["type"])}</span>'
        source_html = f'<div class="src">{html.escape(it["source"])}</div>' if it['source'] else ''
        cards.append(CARD_TMPL.format(
            link=it['link'], num=it['num'], title=html.escape(it['title']),
            sub=html.escape(it['sub']), tags=tags, source_html=source_html,
            subject=html.escape(it['subject']), chapter=html.escape(it['chapter']),
            knowledge=html.escape(it['knowledge']),
        ))
    cards_html = '\n'.join(cards) if cards else '    <div class="empty">暂无课件</div>'

    today = datetime.now().strftime('%Y-%m-%d')
    page = PAGE_TMPL.format(
        count=len(items), subject_count=len(subjects), chapter_count=len(chapters),
        subject_options=opts(subjects), chapter_options=opts(chapters),
        knowledge_options=opts(knowledges), cards=cards_html, date=today,
    )
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(page)
    print(f'OK: 共 {len(items)} 个课件 → index.html ({len(page)/1024:.0f} KB)')


if __name__ == '__main__':
    main()
