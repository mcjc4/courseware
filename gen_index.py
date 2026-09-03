#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
courseware-site 导航首页生成器
用法：在 courseware-site 根目录运行  python gen_index.py
约定：每课一个目录 lessons/<序号>-<英文短名>/index.html
      <title> 建议格式「主标题 · 副标题」（无「·」则整体作为标题）
产出：根目录 index.html（Fresh Gradient 教育风课件导航页）
"""
import os, re, glob, html
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
LESSONS_DIR = os.path.join(ROOT, 'lessons')
OUT = os.path.join(ROOT, 'index.html')


def extract_title(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            head = f.read(200000)
    except Exception:
        return '未命名课件', ''
    m = re.search(r'<title[^>]*>(.*?)</title>', head, re.S | re.I)
    if not m:
        return '未命名课件', ''
    t = html.unescape(re.sub(r'\s+', ' ', m.group(1))).strip()
    if '·' in t:
        main, _, sub = t.partition('·')
        return main.strip(), sub.strip()
    return t, ''


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
        title, sub = extract_title(idx_path)
        mtime = datetime.fromtimestamp(os.path.getmtime(idx_path)).strftime('%Y-%m-%d')
        items.append({
            'order': order,
            'num': num.group(1).zfill(2) if num else '',
            'link': 'lessons/' + name + '/',
            'title': title,
            'sub': sub or '互动解题课件',
            'date': mtime,
        })
    items.sort(key=lambda x: x['order'])
    for i, it in enumerate(items, 1):
        it.setdefault('num', str(i).zfill(2))
    return items


CARD_TMPL = """
    <a class="card" href="{link}" target="_blank" rel="noopener">
      <span class="badge">{num}</span>
      <div class="card-body">
        <h3>{title}</h3>
        <p>{sub}</p>
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
  .wrap {{ max-width:1060px; margin:0 auto; }}
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
  .hero p {{ margin-top:12px; font-size:15px; opacity:.95; line-height:1.7; max-width:640px; }}
  .stat {{ display:flex; gap:26px; margin-top:24px; }}
  .stat div {{ background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.3); border-radius:14px; padding:10px 18px; }}
  .stat b {{ font-size:22px; display:block; }}
  .stat span {{ font-size:12px; opacity:.92; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:18px; margin-top:26px; }}
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
  .card-body {{ min-width:0; }}
  .card-body h3 {{ font-size:16px; color:#1f2d3d; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
  .card-body p {{ font-size:13px; color:#5c7185; margin-top:5px; line-height:1.5; }}
  .go {{
    display:inline-block; margin-top:10px; font-size:13px; color:#fff;
    background:linear-gradient(120deg,#4f8ef7,#22c3a6);
    padding:5px 14px; border-radius:999px;
  }}
  .foot {{ text-align:center; margin-top:34px; font-size:12px; color:#93a7ba; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <span class="tag">互动解题课件库 · 单文件离线可用</span>
    <h1>高考解题课件库</h1>
    <p>Fresh Gradient 教育风互动课件：拖拽演示、逐步推导、KaTeX 公式渲染，全部内嵌单文件，可离线打开。</p>
    <div class="stat">
      <div><b>{count}</b><span>个课件</span></div>
      <div><b>6 科</b><span>覆盖高考学科</span></div>
      <div><b>单文件</b><span>零依赖离线运行</span></div>
    </div>
  </div>
  <div class="grid">
{cards}
  </div>
  <div class="foot">mcjc4 · GitHub Pages · 页面生成于 {date}</div>
</div>
</body>
</html>"""


def main():
    items = scan_lessons()
    cards = '\n'.join(
        CARD_TMPL.format(**it) for it in items
    ) if items else '    <p style="padding:20px;color:#5c7185">暂无课件，往 lessons/ 下添加目录后重新运行本脚本。</p>'
    today = datetime.now().strftime('%Y-%m-%d')
    page = PAGE_TMPL.format(count=len(items), cards=cards, date=today)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(page)
    print(f'OK: 共 {len(items)} 个课件 → index.html ({len(page)/1024:.0f} KB)')


if __name__ == '__main__':
    main()
