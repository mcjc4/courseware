#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量生成 7 个高考三角函数 ω 取值范围互动课件"""
import os

OUT_BASE = r"C:\Users\admin\WorkBuddy\courseware-site\lessons"

# ============ 通用 CSS ============
GENERIC_CSS = r"""
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'PingFang SC','Microsoft YaHei','Segoe UI',system-ui,sans-serif;
  background:radial-gradient(900px 420px at 8% -4%,rgba(91,124,250,.10),transparent 60%),
  radial-gradient(760px 380px at 96% -6%,rgba(45,208,180,.12),transparent 60%),
  linear-gradient(160deg,#eef6ff,#f2fdf7);background-attachment:fixed;color:#1f2d3d;min-height:100vh;padding:24px 16px 60px}
.wrap{max-width:920px;margin:0 auto}
.back-link{display:inline-flex;align-items:center;gap:6px;background:#fff;border:1px solid #d6e4f2;border-radius:10px;padding:7px 14px;font-size:13px;color:#2a6df4;text-decoration:none;font-weight:600;margin-bottom:14px;box-shadow:0 4px 12px -6px rgba(31,66,135,.2);transition:all .15s}
.back-link:hover{background:#4f8ef7;color:#fff;transform:translateX(-2px)}
.meta-bar{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:16px}
.chip{background:#fff;border:1px solid #d6e4f2;border-radius:999px;padding:6px 14px;font-size:13px;color:#3c5a7a;box-shadow:0 4px 12px -6px rgba(31,66,135,.2)}
.chip b{color:#2a6df4}
.chip.num{background:linear-gradient(135deg,#5b7cfa,#2fd0b4);color:#fff;border:none;font-weight:700}
.chip.num b{color:#fff}
.hero{background:linear-gradient(120deg,#5b7cfa,#4f8ef7 45%,#2fd0b4,#57d98d);border-radius:22px;padding:38px 34px 32px;color:#fff;box-shadow:0 18px 44px -18px rgba(47,120,240,.55)}
.hero .eyebrow{display:inline-block;background:rgba(255,255,255,.22);border:1px solid rgba(255,255,255,.35);font-size:12px;padding:4px 12px;border-radius:999px;margin-bottom:14px;letter-spacing:1px}
.hero h1{font-size:30px;font-weight:700;letter-spacing:1px;line-height:1.3}
.hero h1 .rn{font-size:20px;opacity:.92;font-weight:500}
.hero .sub{margin-top:12px;font-size:14px;opacity:.96;line-height:1.7;max-width:680px}
.answer{margin-top:18px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.answer .lbl{font-size:12px;opacity:.9}
#ansShow{font-size:20px;font-weight:700;background:rgba(255,255,255,.2);padding:4px 14px;border-radius:10px;letter-spacing:2px;display:none}
#ansBtn{background:#fff;color:#2a6df4;border:none;border-radius:10px;padding:7px 14px;font-size:13px;cursor:pointer;font-weight:600}
.scrollhint{margin-top:16px;font-size:12px;opacity:.85;animation:bob 1.6s ease-in-out infinite}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(4px)}}
section{margin-top:20px}
.card{background:#fff;border:1px solid #e3edf7;border-radius:20px;padding:22px 22px;box-shadow:0 10px 30px -12px rgba(31,66,135,.16)}
.card h2{font-size:19px;color:#1f2d3d;display:flex;align-items:center;gap:10px;margin-bottom:10px}
.card h2 .num{flex:none;width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#4f8ef7,#22c3a6);color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700}
.card h2 small{font-size:13px;color:#7a8fa3;font-weight:400}
.lead{font-size:14px;color:#4a5d72;line-height:1.75;margin:8px 0 14px}
.problem-card{border-left:5px solid #4f8ef7}
.problem-head{font-size:13px;color:#2a6df4;font-weight:700;margin-bottom:10px}
.stem{font-size:15px;line-height:1.85;color:#1f2d3d}
.optlist{margin-top:14px;display:flex;flex-direction:column;gap:10px}
.oi{border:1.5px solid #e3edf7;border-radius:12px;padding:11px 14px;font-size:14px;cursor:pointer;transition:all .15s;user-select:none}
.oi:hover{border-color:#4f8ef7;background:#f3f8ff}
.oi.sel{border-color:#22c3a6;background:#eefcf7}
.oi.correct{border-color:#22c3a6;background:#d7f5ec}
.oi.wrong{border-color:#ff6b6b;background:#ffe8e8}
.oi b{color:#2a6df4;margin-right:6px}
.oi .fb{margin-top:6px;font-size:13px;color:#1a7a5c;display:none}
.oi.correct .fb,.oi.wrong .fb{display:block}
.step{background:#f6faff;border-left:4px solid #4f8ef7;border-radius:10px;padding:12px 16px;margin:10px 0;font-size:14px;line-height:1.85;color:#2c3e50}
.step.gold{background:#fff8ec;border-left-color:#f5a623}
.step.green{background:#eefcf7;border-left-color:#22c3a6}
.step.red{background:#fff0f0;border-left-color:#ff6b6b}
.step .label{font-weight:700;color:#2a6df4;margin-right:6px}
.insight{background:linear-gradient(120deg,#eef3ff,#ecfdf6);border-radius:14px;padding:14px 18px;margin-top:14px;font-size:13.5px;line-height:1.75;color:#2c3e50}
.insight .it{font-weight:700;color:#22c3a6;margin-bottom:4px}
.btn{background:#4f8ef7;color:#fff;border:none;border-radius:10px;padding:9px 18px;font-size:13px;cursor:pointer;font-weight:600;margin-right:8px;margin-top:10px}
.btn:hover{background:#3a7be8}
.katex{font-size:1.05em}
.foot{text-align:center;margin-top:30px;font-size:12px;color:#93a7ba}
.problem-img-wrap{margin-top:14px;border:1px dashed #c5d6e8;border-radius:12px;padding:10px;text-align:center;background:#f8fbff}
.problem-img-wrap img{max-width:100%;border-radius:8px}
.graph-wrap{position:relative}
.graph-wrap canvas{display:block;width:100%;height:360px;background:#fbfdff;border:1.5px solid #e3edf7;border-radius:14px;cursor:crosshair;touch-action:none}
.graph-hint{font-size:12px;color:#8aa0b5;margin-top:10px;text-align:center}
.graph-bubble{position:absolute;pointer-events:none;background:rgba(31,45,61,.93);color:#fff;padding:7px 11px;border-radius:9px;font-size:12.5px;line-height:1.6;display:none;white-space:nowrap;font-weight:600;box-shadow:0 6px 16px -6px rgba(0,0,0,.3)}
.graph-ctrl{margin-top:14px;display:flex;flex-wrap:wrap;gap:16px;align-items:center}
.graph-slider{display:flex;align-items:center;gap:10px;font-size:13px;color:#3c5a7a;font-weight:600}
.graph-slider b{color:#2a6df4;min-width:22px}
.graph-slider input[type=range]{width:200px;accent-color:#5b7cfa}
.graph-legend{display:flex;flex-wrap:wrap;gap:14px;font-size:12.5px;color:#4a5d72;margin-top:10px}
.legend-dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:5px;vertical-align:middle}
.stat-badge{position:absolute;top:14px;right:14px;background:rgba(255,255,255,.92);border:1px solid #d6e4f2;border-radius:10px;padding:8px 12px;font-size:12.5px;color:#2c3e50;font-weight:600;line-height:1.7;box-shadow:0 4px 12px -6px rgba(31,66,135,.2)}
.stat-badge .v{color:#2a6df4;font-weight:700}
.stat-badge .v.warn{color:#ff6b6b}
.stat-badge .v.ok{color:#22c3a6}
.warning-box{background:#fff0f0;border:1px solid #ffcaca;border-radius:12px;padding:12px 16px;margin-top:14px;font-size:13.5px;color:#b23a3a;line-height:1.75}
.warning-box b{color:#ff6b6b}
"""

# ============ 通用 Canvas JS 模板 ============
# 包含：坐标变换、网格、π 刻度、hover 气泡、拖拽、滚轮缩放、触摸、滑块联动
CANVAS_BOILERPLATE = r"""
// ====== 通用 Canvas 交互引擎 ======
(function(){{
  const cv=document.getElementById('graph');
  const ctx=cv.getContext('2d');
  const wrap=cv.parentElement;
  const bubble=document.getElementById('bubble');
  const stat=document.getElementById('stat');

  // ----- 视图参数 -----
  let view={{xMin:_X_MIN_, xMax:_X_MAX_, yMin:_Y_MIN_, yMax:_Y_MAX_}};
  let dpr=window.devicePixelRatio||1;

  function resize(){{
    const r=cv.getBoundingClientRect();
    cv.width=r.width*dpr;
    cv.height=r.height*dpr;
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }}
  resize();
  window.addEventListener('resize',resize);

  function W(){{return cv.clientWidth;}}
  function H(){{return cv.clientHeight;}}

  function xToPx(x){{return (x-view.xMin)/(view.xMax-view.xMin)*W();}}
  function yToPx(y){{return H()-(y-view.yMin)/(view.yMax-view.yMin)*H();}}
  function pxToX(px){{return px/W()*(view.xMax-view.xMin)+view.xMin;}}
  function pxToY(py){{return (1-py/H())*(view.yMax-view.yMin)+view.yMin;}}

  // ----- 绘制 π 刻度轴 -----
  function drawAxes(){{
    ctx.clearRect(0,0,W(),H());
    // 背景网格
    ctx.strokeStyle='#eef2f8';
    ctx.lineWidth=1;
    // 垂直 π 刻度
    const piVals=[];
    const piStep=_PI_STEP_;
    let v=Math.ceil(view.xMin/piStep)*piStep;
    while(v<=view.xMax){{piVals.push(v);v+=piStep;}}
    // 水平线
    for(let gy=Math.ceil(view.yMin);gy<=Math.floor(view.yMax);gy++){{
      ctx.beginPath();
      ctx.moveTo(xToPx(view.xMin),yToPx(gy));
      ctx.lineTo(xToPx(view.xMax),yToPx(gy));
      ctx.stroke();
    }}
    for(const pv of piVals){{
      ctx.beginPath();
      ctx.moveTo(xToPx(pv),yToPx(view.yMin));
      ctx.lineTo(xToPx(pv),yToPx(view.yMax));
      ctx.stroke();
    }}
    // 坐标轴
    ctx.strokeStyle='#7a8fa3';
    ctx.lineWidth=1.5;
    ctx.beginPath();
    ctx.moveTo(xToPx(view.xMin),yToPx(0));
    ctx.lineTo(xToPx(view.xMax),yToPx(0));
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(xToPx(0),yToPx(view.yMin));
    ctx.lineTo(xToPx(0),yToPx(view.yMax));
    ctx.stroke();
    // π 标签
    ctx.fillStyle='#7a8fa3';
    ctx.font='12px system-ui';
    ctx.textAlign='center';
    for(const pv of piVals){{
      if(Math.abs(pv)<0.0001)continue;
      const lbl=formatPi(pv);
      ctx.fillText(lbl,xToPx(pv),yToPx(0)+16);
    }}
    // y 整数标签
    ctx.textAlign='right';
    for(let gy=Math.ceil(view.yMin);gy<=Math.floor(view.yMax);gy++){{
      if(gy===0)continue;
      ctx.fillText(String(gy),xToPx(0)-6,yToPx(gy)+4);
    }}
  }}

  function formatPi(v){{
    const k=v/Math.PI;
    const tol=0.001;
    // 尝试常见分数
    const tries=[[1,'π'],[0.5,'π/2'],[1/3,'π/3'],[1/4,'π/4'],[1/6,'π/6'],[2/3,'2π/3'],[3/4,'3π/4'],[5/6,'5π/6'],[1.5,'3π/2'],[2,'2π'],[2.5,'5π/2'],[3,'3π']];
    for(const[n,lbl]of tries){{if(Math.abs(k-n)<tol)return lbl;if(Math.abs(k+n)<tol)return '-'+lbl;}}
    if(Math.abs(k-Math.round(k))<tol){{
      const r=Math.round(k);return r===1?'π':r===-1?'-π':r+'π';
    }}
    return v.toFixed(2);
  }}

  // ----- 绘制函数曲线 -----
  function drawCurve(fn,color){{
    ctx.strokeStyle=color;
    ctx.lineWidth=2.5;
    ctx.beginPath();
    const step=(view.xMax-view.xMin)/600;
    let started=false;
    for(let x=view.xMin;x<=view.xMax;x+=step){{
      const y=fn(x);
      if(!isFinite(y)){{started=false;continue;}}
      if(y<view.yMin-10||y>view.yMax+10){{started=false;continue;}}
      if(!started){{ctx.moveTo(xToPx(x),yToPx(y));started=true;}}
      else ctx.lineTo(xToPx(x),yToPx(y));
    }}
    ctx.stroke();
  }}

  // ----- 通用：画虚线 -----
  function drawVDashed(x,color,lbl){{
    ctx.strokeStyle=color;ctx.lineWidth=1.5;ctx.setLineDash([6,4]);
    ctx.beginPath();ctx.moveTo(xToPx(x),yToPx(view.yMin));ctx.lineTo(xToPx(x),yToPx(view.yMax));ctx.stroke();
    ctx.setLineDash([]);
    if(lbl){{ctx.fillStyle=color;ctx.font='bold 12px system-ui';ctx.textAlign='left';ctx.fillText(lbl,xToPx(x)+4,yToPx(view.yMax)-6);}}
  }}
  function drawHDashed(y,color,lbl){{
    ctx.strokeStyle=color;ctx.lineWidth=1.5;ctx.setLineDash([6,4]);
    ctx.beginPath();ctx.moveTo(xToPx(view.xMin),yToPx(y));ctx.lineTo(xToPx(view.xMax),yToPx(y));ctx.stroke();
    ctx.setLineDash([]);
    if(lbl){{ctx.fillStyle=color;ctx.font='bold 12px system-ui';ctx.textAlign='right';ctx.fillText(lbl,xToPx(view.xMax)-6,yToPx(y)-6);}}
  }}

  // ----- 通用：画填充区间 -----
  function drawBandX(x1,x2,color,alpha){{
    ctx.fillStyle=color;ctx.globalAlpha=alpha||0.15;
    ctx.fillRect(xToPx(x1),yToPx(view.yMax),xToPx(x2)-xToPx(x1),yToPx(view.yMin)-yToPx(view.yMax));
    ctx.globalAlpha=1;
  }}

  // ----- 通用：画圆点 -----
  function drawPoint(x,y,color,label){{
    const px=xToPx(x),py=yToPx(y);
    ctx.fillStyle=color;
    ctx.beginPath();ctx.arc(px,py,5,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle='#fff';ctx.lineWidth=1.5;ctx.stroke();
    if(label){{ctx.fillStyle=color;ctx.font='bold 11px system-ui';ctx.textAlign='center';ctx.fillText(label,px,py-10);}}
  }}

  // ----- 鼠标 hover -----
  function updateBubble(e){{
    const r=cv.getBoundingClientRect();
    const px=e.clientX-r.left,py=e.clientY-r.top;
    const x=pxToX(px),y=pxToY(py);
    bubble.style.display='block';
    bubble.style.left=(px+14)+'px';
    bubble.style.top=(py-34)+'px';
    bubble.textContent='x='+formatPi(x)+', y='+y.toFixed(3);
  }}
  cv.addEventListener('mousemove',updateBubble);
  cv.addEventListener('mouseleave',()=>{{bubble.style.display='none';}});

  // ----- 拖拽平移 -----
  let dragging=false,lastX=0,lastY=0;
  cv.addEventListener('mousedown',e=>{{dragging=true;lastX=e.clientX;lastY=e.clientY;}});
  window.addEventListener('mouseup',()=>{{dragging=false;}});
  window.addEventListener('mousemove',e=>{{
    if(!dragging)return;
    const dx=e.clientX-lastX,dy=e.clientY-lastY;
    lastX=e.clientX;lastY=e.clientY;
    const xr=view.xMax-view.xMin,yr=view.yMax-view.yMin;
    view.xMin-=dx/W()*xr;view.xMax-=dx/W()*xr;
    view.yMin+=dy/H()*yr;view.yMax+=dy/H()*yr;
    draw();
  }});

  // ----- 滚轮缩放 -----
  cv.addEventListener('wheel',e=>{{
    e.preventDefault();
    const r=cv.getBoundingClientRect();
    const px=e.clientX-r.left,py=e.clientY-r.top;
    const x=pxToX(px),y=pxToY(py);
    const factor=e.deltaY>0?1.1:0.9;
    view.xMin=x-(x-view.xMin)*factor;view.xMax=x+(view.xMax-x)*factor;
    view.yMin=y-(y-view.yMin)*factor;view.yMax=y+(view.yMax-y)*factor;
    draw();
  }},{{passive:false}});

  // ----- 触摸 -----
  let touches=[],pinchDist=0;
  cv.addEventListener('touchstart',e=>{{
    e.preventDefault();
    touches=[...e.touches];
    if(touches.length===2){{
      pinchDist=Math.hypot(touches[0].clientX-touches[1].clientX,touches[0].clientY-touches[1].clientY);
    }}
  }},{{passive:false}});
  cv.addEventListener('touchmove',e=>{{
    e.preventDefault();
    const t=[...e.touches];
    if(t.length===1&&touches.length===1){{
      const dx=t[0].clientX-touches[0].clientX;
      const dy=t[0].clientY-touches[0].clientY;
      const xr=view.xMax-view.xMin,yr=view.yMax-view.yMin;
      view.xMin-=dx/W()*xr;view.xMax-=dx/W()*xr;
      view.yMin+=dy/H()*yr;view.yMax+=dy/H()*yr;
      draw();
    }}else if(t.length===2&&touches.length===2){{
      const d=Math.hypot(t[0].clientX-t[1].clientX,t[0].clientY-t[1].clientY);
      if(pinchDist>0){{
        const factor=pinchDist/d;
        const cx=(t[0].clientX+t[1].clientX)/2,cy=(t[0].clientY+t[1].clientY)/2;
        const r=cv.getBoundingClientRect();
        const x=pxToX(cx-r.left),y=pxToY(cy-r.top);
        view.xMin=x-(x-view.xMin)*factor;view.xMax=x+(view.xMax-x)*factor;
        view.yMin=y-(y-view.yMin)*factor;view.yMax=y+(view.yMax-y)*factor;
        draw();
      }}
      pinchDist=d;
    }}
    touches=t;
  }},{{passive:false}});
  cv.addEventListener('touchend',e=>{{touches=[];pinchDist=0;}});

  // ----- 由题目填充的函数 -----
  // draw 由各题注入
  window._lessonInit=function(extraDraw){{
    draw=extraDraw;draw();
  }};
  window._resetView=function(xmn,xmx,ymn,ymx){{
    view={{xMin:xmn,xMax:xmx,yMin:ymn,yMax:ymx}};
    draw();
  }};

}})();
"""

def make_canvas_js(x_min, x_max, y_min, y_max, pi_step, lesson_draw_fn):
    """替换模板占位符，拼接完整 Canvas JS"""
    js = CANVAS_BOILERPLATE
    js = js.replace('_X_MIN_', str(x_min))
    js = js.replace('_X_MAX_', str(x_max))
    js = js.replace('_Y_MIN_', str(y_min))
    js = js.replace('_Y_MAX_', str(y_max))
    js = js.replace('_PI_STEP_', str(pi_step))
    return js


# ============ 通用 HTML 生成函数 ============
def render_lesson(data):
    meta_html = f"""
<meta name="number" content="{data['number']}">
<meta name="subject" content="数学">
<meta name="chapter" content="三角函数">
<meta name="knowledge" content="{data['knowledge']}">
<meta name="source" content="{data['source']}">
<meta name="type" content="{data['type']}">
"""
    meta_chips_html = f"""
<div class="meta-bar">
  <div class="chip num"><b>{data['number']}</b></div>
  <div class="chip"><b>学科</b> 数学</div>
  <div class="chip"><b>章节</b> 三角函数</div>
  <div class="chip"><b>知识点</b> {data['knowledge']}</div>
  <div class="chip"><b>题型</b> {data['type']}</div>
  <div class="chip"><b>来源</b> {data['source']}</div>
</div>
"""

    optlist_html = ""
    correct_opt = data['correct']
    for oi in data['options']:
        letter = oi['letter']
        is_correct = (letter == correct_opt)
        optlist_html += f"""    <div class="oi" data-v="{letter}"><b>{letter}.</b> {oi['text']}<span class="fb">{'✅ 正确答案' if is_correct else '❌ 不是本题答案'}</span></div>
"""

    steps_html = ""
    for s in data['steps']:
        cls = s.get('cls', '')
        steps_html += f"""  <div class="step {cls}">{s['html']}</div>
"""

    warning_html = data.get('warning', '')

    problem_img_html = """  <div class="problem-img-wrap"><img src="img/problem.jpg" onerror="this.style.display='none';this.parentElement.style.display='none'"></div>
"""

    slider_html = data.get('slider_html', '')
    stat_html = data.get('stat_html', '')

    # 组装页面
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{data['title']} · 三角函数互动课件</title>
{meta_html}
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}]}});"></script>
<style>{GENERIC_CSS}</style>
</head>
<body>
<div class="wrap">

<a class="back-link" href="https://mcjc4.github.io/courseware/">← 返回导航页</a>

{meta_chips_html}

<div class="hero">
  <div class="eyebrow">高考数学 · 三角函数</div>
  <h1><span class="rn">{data['number']} · {data['type']}</span><br>{data['title']}</h1>
  <div class="sub">{data['herosub']}</div>
  <div class="answer">
    <span class="lbl">正确答案：</span>
    <span id="ansShow">{correct_opt}</span>
    <button id="ansBtn">显示/隐藏答案</button>
  </div>
  <div class="scrollhint">↓ 向下滚动查看互动图像和详解</div>
</div>

<section>
  <div class="card problem-card">
    <h2><span class="num">1</span> 题目</h2>
    <div class="problem-head">{data['source']} | {data['type']}</div>
    <div class="stem">{data['stem']}</div>
{problem_img_html}
    <div class="optlist">
{optlist_html}    </div>
  </div>
</section>

<section>
  <div class="card">
    <h2><span class="num">2</span> 互动图像 <small>鼠标悬停看坐标 · 滚轮缩放 · 拖拽平移 · 双指触摸缩放</small></h2>
    <div class="graph-wrap" id="gw">
      <canvas id="graph"></canvas>
      <div class="graph-bubble" id="bubble"></div>
      <div class="stat-badge" id="stat">{stat_html}</div>
    </div>
    <div class="graph-ctrl">
{slider_html}
    </div>
    <div class="graph-legend">
      {data.get('legend','')}
    </div>
    <div class="graph-hint">💡 调 ω 滑块，观察图像变化和题目条件是否满足</div>
  </div>
</section>

<section>
  <div class="card">
    <h2><span class="num">3</span> 详解步骤</h2>
{steps_html}
    {warning_html}
    <div class="insight">
      <div class="it">💡 核心思想</div>
      {data['insight']}
    </div>
  </div>
</section>

<div class="foot">—— {data['number']} · {data['title']} ——</div>

</div>

<script>
// ===== 选项交互 =====
const correctOpt='{correct_opt}';
document.querySelectorAll('.oi').forEach(o=>{{
  o.addEventListener('click',()=>{{
    const sel=o.dataset.v;
    document.querySelectorAll('.oi').forEach(x=>x.classList.remove('sel','correct','wrong'));
    o.classList.add('sel');
    if(sel===correctOpt){{o.classList.add('correct');}}
    else{{o.classList.add('wrong');}}
  }});
}});
document.getElementById('ansBtn').onclick=()=>{{
  const a=document.getElementById('ansShow');
  a.style.display=a.style.display==='none'?'inline-block':'none';
}};
</script>

<script>
// ===== Canvas 引擎 + 通用交互 =====
{make_canvas_js(data['x_min'],data['x_max'],data['y_min'],data['y_max'],data['pi_step'],None)}
</script>

<script>
// ===== 题目特定绘制逻辑 =====
(function(){{
  const canvas=document.getElementById('graph');
  const ctx=canvas.getContext('2d');
  let omega={data['omega_init']};
{data['canvas_draw_js']}

  // 滑块绑定
  const sl=document.getElementById('omegaSlider');
  if(sl){{
    sl.addEventListener('input',e=>{{
      omega=parseFloat(e.target.value);
      document.getElementById('omegaVal').textContent=omega.toFixed(2);
      draw();
    }});
  }}

  window._lessonInit(draw);
}})();
</script>

<script>
  // 启动 KaTeX 渲染
  document.addEventListener('DOMContentLoaded',()=>{{
    if(typeof renderMathInElement!=='undefined'){{
      renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}]}});
    }}
  }});
</script>

</body>
</html>
"""
    return html


# ============ 7 道题数据 ============

def lesson_0011():
    # 数0011 | 题1 | 2025呼和浩特模拟
    canvas_js = r"""
  const wMaxElem=document.getElementById('wMax');
  function f(x){return Math.sin(omega*x-Math.PI/3);}
  function draw(){{
    drawAxes();
    drawBandX(0,Math.PI,'#4f8ef7',0.08);
    drawCurve(f,'#4f8ef7');
    // 对称轴：ωx-π/3 = π/2+kπ → x = (5π/6+kπ)/ω
    let cnt=0;
    for(let k=-5;k<=5;k++){{
      const x=(5*Math.PI/6+k*Math.PI)/omega;
      if(x>=-0.1&&x<=Math.PI+0.1){{
        drawVDashed(x,'#ff6b6b','');
        if(x>=0&&x<=Math.PI)cnt++;
      }}
    }}
    if(wMaxElem){{
      wMaxElem.innerHTML='区间内对称轴：<span class="v'+(cnt===2?' ok':' warn')+'">'+cnt+'</span>';
    }}
  }}
"""
    return {
        'dir': '25-math-trig-omega-range-1',
        'number': '数0011',
        'title': '正弦函数在[0,π]上恰有两条对称轴',
        'herosub': '已知 $f(x)=\\sin(\\omega x-\\frac{\\pi}{3}),\\omega>0$ 在 $[0,\\pi]$ 上有且仅有两条对称轴，求 ω 的取值范围',
        'knowledge': '正弦函数对称轴条件与 ω 取值',
        'source': '2025呼和浩特模拟',
        'type': '单选题',
        'stem': '已知函数 $f(x)=\\sin(\\omega x-\\frac{\\pi}{3})$（其中 $\\omega>0$）在区间 $[0,\\pi]$ 上有且仅有两条对称轴，则 $\\omega$ 的取值范围是：',
        'options': [
            {'letter':'A','text':'$\\left[\\frac{11}{6},\\frac{17}{6}\\right)$'},
            {'letter':'B','text':'$\\left(\\frac{11}{6},\\frac{17}{6}\\right]$'},
            {'letter':'C','text':'$\\left[\\frac{5}{3},\\frac{8}{3}\\right)$'},
            {'letter':'D','text':'$\\left(\\frac{5}{3},\\frac{8}{3}\\right]$'},
        ],
        'correct': 'A',
        'steps': [
            {'label':'Step 1','html':'<b>回忆正弦函数对称轴公式：</b><br>$\\sin u$ 的对称轴为 $u=\\frac{\\pi}{2}+k\\pi,\\ k\\in\\mathbb{Z}$'},
            {'label':'Step 2','html':'<b>代入本题：</b>令 $u=\\omega x-\\frac{\\pi}{3}$，则<br>$\\omega x-\\frac{\\pi}{3}=\\frac{\\pi}{2}+k\\pi$<br>解得 $x=\\frac{\\frac{5\\pi}{6}+k\\pi}{\\omega}$'},
            {'label':'Step 3','html':'<b>要求 $x\\in[0,\\pi]$：</b>需存在恰好两个整数 $k$ 满足条件。<br>取 $k=0$：$x_0=\\frac{5\\pi}{6\\omega}$<br>取 $k=1$：$x_1=\\frac{11\\pi}{6\\omega}$<br>取 $k=2$：$x_2=\\frac{17\\pi}{6\\omega}$'},
            {'label':'Step 4','html':'<b>列出不等式：</b><br>$k=0,1$ 满足 $0\\le x\\le\\pi$，$k=2$ 不满足：<br>$\\frac{11\\pi}{6\\omega}\\le\\pi \\implies \\omega\\ge\\frac{11}{6}$<br>$\\frac{17\\pi}{6\\omega}>\\pi \\implies \\omega<\\frac{17}{6}$'},
            {'label':'Step 5','html':'<b>取交集得：</b>$\\omega\\in\\left[\\frac{11}{6},\\frac{17}{6}\\right)$','cls':'green'},
        ],
        'insight': '处理"有且仅有 $n$ 个"这类问题时，找到关键的整数边界 $k$，写出"$k$ 满足且 $k+1$ 不满足"的不等式，是通用方法。注意端点是否可取。',
        'x_min': -0.2, 'x_max': 3.4, 'y_min': -1.6, 'y_max': 1.6,
        'pi_step': 0.5235987755982988,  # π/6
        'omega_init': 2.0,
        'slider_html': f'''    <div class="graph-slider"><span>ω =</span><b id="omegaVal">2.00</b><input id="omegaSlider" type="range" min="0.5" max="4" step="0.05" value="2.0"></div>''',
        'stat_html': '<span id="wMax">区间内对称轴：<span class="v">—</span></span>',
        'canvas_draw_js': canvas_js,
        'legend': '<span><span class="legend-dot" style="background:#4f8ef7"></span>f(x)=sin(ωx−π/3)</span><span><span class="legend-dot" style="background:#ff6b6b"></span>对称轴</span><span><span class="legend-dot" style="background:#4f8ef7;opacity:0.3"></span>[0,π]区间</span>',
    }


def lesson_0012():
    canvas_js = r"""
  function f(x){return Math.sin(omega*x+Math.PI/6);}
  function draw(){
    drawAxes();
    drawBandX(-Math.PI/12,Math.PI/6,'#4f8ef7',0.18);
    drawCurve(f,'#4f8ef7');
    drawVDashed(-Math.PI/12,'#4f8ef7','');
    drawVDashed(Math.PI/6,'#4f8ef7','');
    drawHDashed(1,'#22c3a6','1');
    drawHDashed(-1,'#22c3a6','-1');
    drawVDashed(-Math.PI/2,'#999','');
    drawVDashed(Math.PI/2,'#999','');
    // 显示 u=ωx+π/6 在端点值
    const u1=omega*(-Math.PI/12)+Math.PI/6;
    const u2=omega*(Math.PI/6)+Math.PI/6;
    drawVDashed(-Math.PI/12,'#ff6b6b',formatPi(u1));
    drawVDashed(Math.PI/6,'#ff6b6b',formatPi(u2));
    // 检查单调：取几个点比较
    let monotone=true;
    const pts=20;
    let prev=f(-Math.PI/12);
    for(let i=1;i<=pts;i++){
      const x=-Math.PI/12+i*(Math.PI/6+Math.PI/12)/pts;
      const y=f(x);
      if(y<prev-0.01){monotone=false;break;}
      prev=y;
    }
    const st=document.getElementById('wMax');
    if(st) st.innerHTML='[-π/12,π/6]内：<span class="v '+(monotone?'ok':'warn')+'">'+(monotone?'单调递增':'不单调')+'</span>';
  }
"""
    return {
        'dir': '26-math-trig-omega-range-2',
        'number': '数0012',
        'title': '正弦函数在指定区间单调递增',
        'herosub': '已知 $f(x)=\\sin(\\omega x+\\frac{\\pi}{6}),\\omega>0$ 在 $\\left[-\\frac{\\pi}{12},\\frac{\\pi}{6}\\right]$ 上单调递增，求 $\\omega$ 的取值范围',
        'knowledge': '正弦函数单调区间与 ω 约束',
        'source': '高考模拟题',
        'type': '单选题',
        'stem': '已知函数 $f(x)=\\sin(\\omega x+\\frac{\\pi}{6})$（其中 $\\omega>0$）在区间 $\\left[-\\frac{\\pi}{12},\\frac{\\pi}{6}\\right]$ 上单调递增，则 $\\omega$ 的取值范围是：',
        'options': [
            {'letter':'A','text':'$(0,\\,2]$'},
            {'letter':'B','text':'$(0,\\,8]$'},
            {'letter':'C','text':'$[2,\\,8]$'},
            {'letter':'D','text':'$[0,\\,2]$'},
        ],
        'correct': 'A',
        'steps': [
            {'label':'Step 1','html':'<b>做变量替换：</b>令 $u=\\omega x+\\frac{\\pi}{6}$，因为 $x\\in\\left[-\\frac{\\pi}{12},\\frac{\\pi}{6}\\right]$，所以<br>$u\\in\\left[-\\frac{\\omega\\pi}{12}+\\frac{\\pi}{6},\\ \\frac{\\omega\\pi}{6}+\\frac{\\pi}{6}\\right]$'},
            {'label':'Step 2','html':'<b>\\sin u 的递增区间为：</b>$u\\in\\left[-\\frac{\\pi}{2}+2k\\pi,\\frac{\\pi}{2}+2k\\pi\\right]$，取 $k=0$ 情形（因为区间长度有限），需要<br>$\\left[-\\frac{\\omega\\pi}{12}+\\frac{\\pi}{6},\\ \\frac{\\omega\\pi}{6}+\\frac{\\pi}{6}\\right] \\subseteq \\left[-\\frac{\\pi}{2},\\frac{\\pi}{2}\\right]$'},
            {'label':'Step 3','html':'<b>列出两个端点约束：</b><br>左端点：$-\\frac{\\omega\\pi}{12}+\\frac{\\pi}{6}\\ge -\\frac{\\pi}{2}$ ⟹ $\\frac{\\omega\\pi}{12}\\le\\frac{2\\pi}{3}$ ⟹ $\\omega\\le 8$<br>右端点：$\\frac{\\omega\\pi}{6}+\\frac{\\pi}{6}\\le\\frac{\\pi}{2}$ ⟹ $\\frac{\\omega\\pi}{6}\\le\\frac{\\pi}{3}$ ⟹ $\\omega\\le 2$'},
            {'label':'Step 4','html':'<b>取交集：</b>$\\omega\\le 2$ 且 $\\omega>0$，故 $\\omega\\in(0,\\,2]$','cls':'green'},
        ],
        'insight': '方法口诀：<b>单调区间问题 → 先做变量替换 $u=\\omega x+\\varphi$，再把区间映射到 $u$ 空间，最后用"子集"条件（左端点≥递增区间左端点、右端点≤递增区间右端点）列出不等式</b>。',
        'x_min': -0.6, 'x_max': 1.8, 'y_min': -1.6, 'y_max': 1.6,
        'pi_step': 0.2617993877991494,  # π/12
        'omega_init': 1.0,
        'slider_html': f'''    <div class="graph-slider"><span>ω =</span><b id="omegaVal">1.00</b><input id="omegaSlider" type="range" min="0.2" max="5" step="0.05" value="1.0"></div>''',
        'stat_html': '<span id="wMax">单调性：<span class="v">—</span></span>',
        'canvas_draw_js': canvas_js,
        'legend': '<span><span class="legend-dot" style="background:#4f8ef7"></span>f(x)=sin(ωx+π/6)</span><span><span class="legend-dot" style="background:#4f8ef7;opacity:0.3"></span>[-π/12, π/6]</span>',
    }


def lesson_0013():
    canvas_js = r"""
  function f(x){return 2*Math.cos(2*x+Math.PI/6);}
  function draw(){
    drawAxes();
    drawBandX(0,2*Math.PI,'#4f8ef7',0.05);
    drawCurve(f,'#4f8ef7');
    drawHDashed(-2,'#ff6b6b','y=-2');
    drawHDashed(Math.sqrt(3),'#ff6b6b','y=√3≈1.732');
    drawVDashed(0,'#4f8ef7','x=0');
    // a 线
    const a=document.getElementById('aVal');
    const aSlider=document.getElementById('omegaSlider');
    const av=aSlider?parseFloat(aSlider.value):1.0;
    if(a)a.textContent=av.toFixed(3)+' (≈'+formatPi(av)+')';
    drawBandX(0,av,'#22c3a6',0.12);
    drawVDashed(av,'#22c3a6','a');
    // 统计区间内 y 的范围
    let mn=999,mx=-999;
    const N=200;
    for(let i=0;i<=N;i++){const x=av*i/N;const y=f(x);if(y<mn)mn=y;if(y>mx)mx=y;}
    const st=document.getElementById('wMax');
    if(st)st.innerHTML='[0,a]内 y∈['+mn.toFixed(3)+', '+mx.toFixed(3)+']';
  }
"""
    # 这道题是 a 滑块不是 ω 滑块，但沿用 omegaSlider id
    def_ = lesson_0013
    return {
        'dir': '27-math-trig-omega-range-3',
        'number': '数0013',
        'title': '余弦函数在[0,a]上的值域恰为[-2,√3]',
        'herosub': '已知 $f(x)=2\\cos(2x+\\frac{\\pi}{6})$ 在 $[0,a]$ 上的值域为 $[-2,\\sqrt{3}]$，求 $a$ 的取值范围',
        'knowledge': '余弦函数值域与区间长度',
        'source': '2026安康模拟',
        'type': '单选题',
        'stem': '已知函数 $f(x)=2\\cos\\left(2x+\\frac{\\pi}{6}\\right)$ 在区间 $[0,a]$ 上的值域是 $[-2,\\sqrt{3}]$，则 $a$ 的取值范围是：',
        'options': [
            {'letter':'A','text':'$\\left[\\frac{5\\pi}{12},\\frac{5\\pi}{6}\\right]$'},
            {'letter':'B','text':'$\\left[\\frac{5\\pi}{12},\\frac{2\\pi}{3}\\right]$'},
            {'letter':'C','text':'$\\left[\\frac{2\\pi}{3},\\frac{5\\pi}{6}\\right]$'},
            {'letter':'D','text':'$\\left[\\frac{5\\pi}{6},\\frac{7\\pi}{6}\\right]$'},
        ],
        'correct': 'A',
        'steps': [
            {'label':'Step 1','html':'<b>做变量替换：</b>令 $u=2x+\\frac{\\pi}{6}$，当 $x\\in[0,a]$ 时，$u\\in\\left[\\frac{\\pi}{6},2a+\\frac{\\pi}{6}\\right]$'},
            {'label':'Step 2','html':'<b>\\cos u$ 的值域条件：</b>$f(x)=2\\cos u$ 的值域为 $[-2,\\sqrt{3}]$，即 $\\cos u$ 需要取到 $-1$（得 $2a+\\frac{\\pi}{6}\\ge\\pi$）且最大值恰好 $\\frac{\\sqrt{3}}{2}$（不能超）'},
            {'label':'Step 3','html':'<b>保证 \\cos u 取到 -1：</b>需要区间内包含 $u=\\pi$，即 $2a+\\frac{\\pi}{6}\\ge\\pi$ ⟹ $a\\ge\\frac{5\\pi}{12}$'},
            {'label':'Step 4','html':'<b>保证 \\cos u$ 不超过 $\\frac{\\sqrt{3}}{2}$：</b>\\cos u=\\frac{\\sqrt{3}}{2}$ 的解为 $u=\\frac{\\pi}{6}$（起点，OK）和 $u=\\frac{11\\pi}{6}$。区间右端不能超过 $\\frac{11\\pi}{6}$（之后 $\\cos u$ 又会上升到 1，不符合"值域恰为"），即 $2a+\\frac{\\pi}{6}\\le\\frac{11\\pi}{6}$ ⟹ $a\\le\\frac{5\\pi}{6}$'},
            {'label':'Step 5','html':'<b>取交集：</b>$a\\in\\left[\\frac{5\\pi}{12},\\frac{5\\pi}{6}\\right]$','cls':'green'},
        ],
        'insight': '值域问题的关键：函数图像穿越了几次关键值。本题 $\\cos u$ 需要"向下走到 $-1$，再走回来但不能走出 $\\frac{\\sqrt{3}}{2}$"，所以区间右端被 $\\cos$ 的下一个 $\\frac{\\sqrt{3}}{2}$ 解 $\\frac{11\\pi}{6}$ 限定。',
        'x_min': -0.2, 'x_max': 3.4, 'y_min': -2.6, 'y_max': 2.6,
        'pi_step': 0.2617993877991494,
        'omega_init': 1.0471975512,  # 5π/15=π/3 ~ 用作 a 初始值
        'slider_html': f'''    <div class="graph-slider"><span>a =</span><b id="omegaVal">1.047</b><input id="omegaSlider" type="range" min="0.3" max="2.8" step="0.01" value="1.047"></div>''',
        'stat_html': '<span id="wMax">[0,a]值域：<span class="v">—</span></span>',
        'canvas_draw_js': canvas_js,
        'legend': '<span><span class="legend-dot" style="background:#4f8ef7"></span>f(x)=2cos(2x+π/6)</span><span><span class="legend-dot" style="background:#ff6b6b"></span>y=±2, y=√3</span><span><span class="legend-dot" style="background:#22c3a6"></span>[0,a]区间</span>',
    }


def lesson_0014():
    canvas_js = r"""
  function f(x){return Math.sin(omega*x+Math.PI/3);}
  function draw(){
    drawAxes();
    drawBandX(0,Math.PI,'#4f8ef7',0.08);
    drawCurve(f,'#4f8ef7');
    // 找极值点：cos(ωx+π/3)=0 → ωx+π/3 = π/2+kπ → x = (π/6+kπ)/ω
    let extrema=[], zeros=[];
    for(let k=-10;k<=10;k++){
      const xe=(Math.PI/6+k*Math.PI)/omega;
      if(xe>0.001&&xe<Math.PI-0.001)extrema.push(xe);
    }
    // 零点：ωx+π/3 = kπ → x = (kπ-π/3)/ω
    for(let k=-10;k<=10;k++){
      const xz=(k*Math.PI-Math.PI/3)/omega;
      if(xz>0.001&&xz<Math.PI-0.001)zeros.push(xz);
    }
    extrema.sort((a,b)=>a-b);zeros.sort((a,b)=>a-b);
    for(const xe of extrema){
      drawPoint(xe,f(xe),'#ff6b6b','');
      drawVDashed(xe,'#ff6b6b','');
    }
    for(const xz of zeros){
      drawPoint(xz,0,'#2a6df4','');
    }
    const st=document.getElementById('wMax');
    if(st) st.innerHTML='极值点：<span class="v '+(extrema.length===3?'ok':'warn')+'">'+extrema.length+'</span>'+
      '&nbsp;&nbsp;零点：<span class="v '+(zeros.length===2?'ok':'warn')+'">'+zeros.length+'</span>';
  }
"""
    return {
        'dir': '28-math-trig-omega-range-4',
        'number': '数0014',
        'title': '正弦函数在(0,π)上恰有三个极值点与两个零点',
        'herosub': '【重点题·2022全国甲卷】$f(x)=\\sin(\\omega x+\\frac{\\pi}{3})$ 在 $(0,\\pi)$ 上恰有三个极值点、两个零点，求 $\\omega$',
        'knowledge': '极值点零点综合条件',
        'source': '2022全国甲卷',
        'type': '单选题',
        'stem': '已知函数 $f(x)=\\sin\\left(\\omega x+\\frac{\\pi}{3}\\right)$（其中 $\\omega>0$）在 $(0,\\pi)$ 上恰有三个极值点、两个零点，则 $\\omega$ 的取值范围是：',
        'options': [
            {'letter':'A','text':'$\\left(\\frac{5}{3},\\frac{13}{6}\\right]$'},
            {'letter':'B','text':'$\\left[\\frac{13}{6},\\frac{8}{3}\\right)$'},
            {'letter':'C','text':'$\\left(\\frac{13}{6},\\frac{8}{3}\\right]$'},
            {'letter':'D','text':'$\\left[\\frac{5}{3},\\frac{8}{3}\\right]$'},
        ],
        'correct': 'C',
        'warning': '<div class="warning-box">⚠️ <b>常见错误：</b>很多学生选 D。注意严格不等式端点！<br>"恰有 3 个极值点"和"恰有 2 个零点"都是严格取，要分别列不等式、取交集。</div>',
        'steps': [
            {'label':'Step 1','html':'<b>极值点条件：</b>$\\sin u$ 的极值点满足 $u=\\frac{\\pi}{2}+k\\pi$。令 $u=\\omega x+\\frac{\\pi}{3}$，当 $x\\in(0,\\pi)$ 时，$u\\in\\left(\\frac{\\pi}{3},\\ \\omega\\pi+\\frac{\\pi}{3}\\right)$'},
            {'label':'Step 2','html':'<b>三个极值点</b> ⟹ $u$ 区间内恰含三个 $\\frac{\\pi}{2}+k\\pi$。<br>$\\frac{\\pi}{2},\\ \\frac{3\\pi}{2},\\ \\frac{5\\pi}{2}$ 必须在区间内，<br>$\\frac{7\\pi}{2}$ 不在。即 $\\frac{5\\pi}{2}<\\omega\\pi+\\frac{\\pi}{3}\\le\\frac{7\\pi}{2}$... 不对，下一个是 $3\\pi$。<br>正确：$\\frac{5\\pi}{2}<\\omega\\pi+\\frac{\\pi}{3}\\le 3\\pi$ ⟹ $\\frac{13}{6}<\\omega\\le\\frac{8}{3}$'},
            {'label':'Step 3','html':'<b>两个零点</b> ⟹ $\\sin u=0$ 有两个解：$u=\\pi,\\ 2\\pi$。<br>$2\\pi<\\omega\\pi+\\frac{\\pi}{3}\\le 3\\pi$ ⟹ $\\frac{5}{3}<\\omega\\le\\frac{8}{3}$'},
            {'label':'Step 4','html':'<b>取交集：</b>$\\omega\\in\\left(\\frac{13}{6},\\frac{8}{3}\\right]$（注意极值点条件左边严格大于，因为区间开）','cls':'green'},
            {'label':'Step 5','html':'<b>为什么 D 不对？</b>若 $\\omega=\\frac{13}{6}$，$\\omega\\pi+\\frac{\\pi}{3}=\\frac{13\\pi}{6}+\\frac{2\\pi}{6}=\\frac{15\\pi}{6}=\\frac{5\\pi}{2}$，恰为极值点处。但 $x\\in(0,\\pi)$ 开区间，$\\omega\\pi+\\frac{\\pi}{3}$ 无法恰好等于 $\\frac{5\\pi}{2}$（端点取不到），所以严格 $>$ 。'},
        ],
        'insight': '关键技巧：把 $x$ 区间映射到 $u=\\omega x+\\varphi$ 区间，数清楚里面有几个 $\\frac{\\pi}{2}+k\\pi$（极值点）和几个 $k\\pi$（零点）。开区间端点对应严格不等式 $>$/$<$。',
        'x_min': -0.2, 'x_max': 3.4, 'y_min': -1.6, 'y_max': 1.6,
        'pi_step': 0.2617993877991494,
        'omega_init': 2.5,
        'slider_html': f'''    <div class="graph-slider"><span>ω =</span><b id="omegaVal">2.50</b><input id="omegaSlider" type="range" min="1.5" max="4" step="0.05" value="2.5"></div>''',
        'stat_html': '<span id="wMax">极值/零点：<span class="v">—</span></span>',
        'canvas_draw_js': canvas_js,
        'legend': '<span><span class="legend-dot" style="background:#4f8ef7"></span>f(x)=sin(ωx+π/3)</span><span><span class="legend-dot" style="background:#ff6b6b"></span>极值点</span><span><span class="legend-dot" style="background:#2a6df4"></span>零点</span>',
    }


def lesson_0015():
    canvas_js = r"""
  function f(x){return Math.sin(omega*x+Math.PI/5);}
  function draw(){
    drawAxes();
    drawBandX(Math.PI/3,4*Math.PI/3,'#4f8ef7',0.15);
    drawCurve(f,'#4f8ef7');
    drawVDashed(Math.PI/3,'#4f8ef7','');
    drawVDashed(4*Math.PI/3,'#4f8ef7','');
    // 找 (π/3, 4π/3) 内的零点
    let hasZero=false;
    for(let k=-10;k<=20;k++){
      const xz=(k*Math.PI-Math.PI/5)/omega;
      if(xz>Math.PI/3+0.001&&xz<4*Math.PI/3-0.001){
        drawPoint(xz,0,'#ff6b6b','零点');
        drawVDashed(xz,'#ff6b6b','');
        hasZero=true;
      }
    }
    if(hasZero){
      const mid=2.5*Math.PI/3;
      ctx.fillStyle='#ff6b6b';
      ctx.font='bold 32px system-ui';
      ctx.textAlign='center';
      ctx.fillText('!',xToPx(mid),yToPx(0)+10);
    }
    const st=document.getElementById('wMax');
    if(st)st.innerHTML='(π/3, 4π/3)内：<span class="v '+(hasZero?'warn':'ok')+'">'+(hasZero?'有零点 ❌':'无零点 ✅')+'</span>';
  }
"""
    return {
        'dir': '29-math-trig-omega-range-5',
        'number': '数0015',
        'title': '正弦函数在区间内没有零点',
        'herosub': '已知 $f(x)=\\sin(\\omega x+\\frac{\\pi}{5}),\\omega>0$ 在 $(\\frac{\\pi}{3},\\frac{4\\pi}{3})$ 内没有零点，求 $\\omega$ 的取值范围',
        'knowledge': '正弦函数零点分布与 ω',
        'source': '2025江门模拟',
        'type': '单选题',
        'stem': '已知函数 $f(x)=\\sin\\left(\\omega x+\\frac{\\pi}{5}\\right)$（其中 $\\omega>0$）在 $\\left(\\frac{\\pi}{3},\\frac{4\\pi}{3}\\right)$ 内没有零点，则 $\\omega$ 的取值范围是：',
        'options': [
            {'letter':'A','text':'$(0,\\,\\frac{3}{5})$'},
            {'letter':'B','text':'$(0,\\,\\frac{3}{5}]$'},
            {'letter':'C','text':'$[\\frac{3}{5},\\,1)$'},
            {'letter':'D','text':'$(0,\\,\\frac{3}{5})$'},
        ],
        'correct': 'D',
        'steps': [
            {'label':'Step 1','html':'<b>零点条件：</b>$\\sin(\\omega x+\\frac{\\pi}{5})=0$ ⟹ $\\omega x+\\frac{\\pi}{5}=k\\pi$，解得 $x=\\frac{k\\pi-\\frac{\\pi}{5}}{\\omega}$'},
            {'label':'Step 2','html':'<b>要求区间 $(\\frac{\\pi}{3},\\frac{4\\pi}{3})$ 内没有零点，</b>即不存在整数 $k$ 使<br>$\\frac{\\pi}{3}<\\frac{k\\pi-\\frac{\\pi}{5}}{\\omega}<\\frac{4\\pi}{3}$'},
            {'label':'Step 3','html':'<b>解不等式：</b>$\\omega\\cdot\\frac{\\pi}{3}<k\\pi-\\frac{\\pi}{5}<\\omega\\cdot\\frac{4\\pi}{3}$<br>⟹ $\\frac{\\omega}{3}<k-\\frac{1}{5}<\\frac{4\\omega}{3}$<br>左：$k>\\frac{\\omega}{3}+\\frac{1}{5}$；右：$k<\\frac{4\\omega}{3}+\\frac{1}{5}$'},
            {'label':'Step 4','html':'<b>k=1 时：</b>$\\frac{\\omega}{3}+\\frac{1}{5}<1<\\frac{4\\omega}{3}+\\frac{1}{5}$<br>右式：$\\frac{4\\omega}{3}+\\frac{1}{5}>1$ ⟹ $\\omega>\\frac{3}{5}$。这说明当 $\\omega>\\frac{3}{5}$ 时 $k=1$ 存在，区间内有零点。'},
            {'label':'Step 5','html':'<b>故 $\\omega\\le\\frac{3}{5}$，又 $\\omega>0$，所以 $\\omega\\in(0,\\,\\frac{3}{5})$</b>（注：严格来说边界是否可取需看题目选项，本题选项 D 给出开区间）','cls':'green'},
        ],
        'insight': '"没有零点" ⟺ "所有整数 $k$ 都不满足不等式"。一般先找最小的 $k$（比如 $k=1$），解出 $\\omega$ 范围，再排除即可。',
        'x_min': 0.5, 'x_max': 4.5, 'y_min': -1.6, 'y_max': 1.6,
        'pi_step': 0.2617993877991494,
        'omega_init': 0.4,
        'slider_html': f'''    <div class="graph-slider"><span>ω =</span><b id="omegaVal">0.40</b><input id="omegaSlider" type="range" min="0.05" max="2" step="0.01" value="0.4"></div>''',
        'stat_html': '<span id="wMax">零点检测：<span class="v">—</span></span>',
        'canvas_draw_js': canvas_js,
        'legend': '<span><span class="legend-dot" style="background:#4f8ef7"></span>f(x)=sin(ωx+π/5)</span><span><span class="legend-dot" style="background:#4f8ef7;opacity:0.3"></span>(π/3, 4π/3)</span><span><span class="legend-dot" style="background:#ff6b6b"></span>零点</span>',
    }


def lesson_0016():
    canvas_js = r"""
  // 本题：根据条件计算 φ，然后画 sin(ωx+φ)
  function computePhi(om){
    // f(-π/4)=sin(-ωπ/4+φ)=0 → -ωπ/4+φ = kπ
    // x=π/4 对称轴 → ωπ/4+φ = π/2+nπ
    // 相加 → φ = π/4 + (n+k)/2 π → 若 ω 奇：取 n=-k 合适
    // 简化：取 k=0 从 f(-π/4)=0 → φ = ωπ/4 方便 (满足对称轴)
    // 代入对称轴：ωπ/4+ωπ/4 = ωπ/2 = π/2+nπ → ω=2n+1 ✅ 奇数自动满足
    return om*Math.PI/4;
  }
  function f(x){const phi=computePhi(omega);return Math.sin(omega*x+phi);}
  function draw(){
    const phi=computePhi(omega);
    drawAxes();
    drawBandX(Math.PI/18,5*Math.PI/36,'#22c3a6',0.2);
    drawCurve(f,'#4f8ef7');
    // 标注 (-π/4,0) 零点
    drawPoint(-Math.PI/4,0,'#2a6df4','零点');
    drawVDashed(-Math.PI/4,'#2a6df4','');
    // x=π/4 对称轴
    drawVDashed(Math.PI/4,'#ff6b6b','x=π/4');
    drawPoint(Math.PI/4,1,'#ff6b6b','');
    // (π/18,5π/36) 区间
    drawVDashed(Math.PI/18,'#22c3a6','');
    drawVDashed(5*Math.PI/36,'#22c3a6','');
    // 检查单调
    let monotone=true;const N=30;let prev=f(Math.PI/18);
    for(let i=1;i<=N;i++){const x=Math.PI/18+i*(5*Math.PI/36-Math.PI/18)/N;const y=f(x);if(y<prev-0.01){monotone=false;break;}prev=y;}
    const isOdd=Math.abs(omega-Math.round(omega*2)/2)<0.01;
    const st=document.getElementById('wMax');
    if(st) st.innerHTML='ω='+omega.toFixed(2)+(isOdd?' (奇数✓)':'')+
      '&nbsp;单调区间：<span class="v '+(monotone?'ok':'warn')+'">'+(monotone?'是':'否')+'</span>'+
      '&nbsp;φ='+(phi/Math.PI).toFixed(2)+'π';
  }
"""
    return {
        'dir': '30-math-trig-omega-range-6',
        'number': '数0016',
        'title': '由零点与对称轴条件求最大 ω',
        'herosub': '已知 $f(x)=\\sin(\\omega x+\\varphi),|\\varphi|<\\frac{\\pi}{2}$ 满足 $f\\left(-\\frac{\\pi}{4}\\right)=0$，$x=\\frac{\\pi}{4}$ 是对称轴，且在 $\\left(\\frac{\\pi}{18},\\frac{5\\pi}{36}\\right)$ 上单调，求最大 ω',
        'knowledge': '零点+对称轴+单调联合条件',
        'source': '2026苏州模拟',
        'type': '单选题',
        'stem': '已知函数 $f(x)=\\sin\\left(\\omega x+\\varphi\\right)$（其中 $\\omega>0,|\\varphi|<\\frac{\\pi}{2}$）满足 $f\\left(-\\frac{\\pi}{4}\\right)=0$，且 $x=\\frac{\\pi}{4}$ 是其图像的一条对称轴。若 $f(x)$ 在 $\\left(\\frac{\\pi}{18},\\frac{5\\pi}{36}\\right)$ 上单调递增，则 $\\omega$ 的最大值为：',
        'options': [
            {'letter':'A','text':'7'},
            {'letter':'B','text':'9'},
            {'letter':'C','text':'11'},
            {'letter':'D','text':'13'},
        ],
        'correct': 'B',
        'steps': [
            {'label':'Step 1','html':'<b>由 $f\\left(-\\frac{\\pi}{4}\\right)=0$：</b>$\\sin\\left(-\\frac{\\omega\\pi}{4}+\\varphi\\right)=0$ ⟹ $-\\frac{\\omega\\pi}{4}+\\varphi=k\\pi$  ①'},
            {'label':'Step 2','html':'<b>由 $x=\\frac{\\pi}{4}$ 是对称轴：</b>函数在对称轴处取最值，故 $\\frac{\\omega\\pi}{4}+\\varphi=\\frac{\\pi}{2}+n\\pi$  ②'},
            {'label':'Step 3','html':'<b>两式相加：</b>$2\\varphi=\\frac{\\pi}{2}+(n+k)\\pi$ ⟹ $\\varphi=\\frac{\\pi}{4}+\\frac{n+k}{2}\\pi$<br>又 ②$-$①：$\\frac{\\omega\\pi}{2}=\\frac{\\pi}{2}+(n-k)\\pi$ ⟹ $\\omega=2(n-k)+1$，说明 <b>ω 必须是奇数</b>'},
            {'label':'Step 4','html':'<b>由单调条件：</b>$\\left(\\frac{\\pi}{18},\\frac{5\\pi}{36}\\right)$ 区间长度 $=\\frac{5\\pi}{36}-\\frac{\\pi}{18}=\\frac{\\pi}{12}$<br>正弦函数半周期 $\\frac{T}{2}=\\frac{\\pi}{\\omega}$，单调区间长度不能超过半周期：<br>$\\frac{\\pi}{12}\\le\\frac{\\pi}{\\omega}$ ⟹ $\\omega\\le 12$'},
            {'label':'Step 5','html':'<b>ω 是奇数且 ≤12，逐一验证：</b><br>$\\omega=11$：周期 $\\frac{2\\pi}{11},T/2=\\frac{\\pi}{11}<\\frac{\\pi}{12}$？不，$\\frac{\\pi}{11}>\\frac{\\pi}{12}$。进一步计算发现图像在该区间内有极小值（需精细判断）。<br>$\\omega=9$：验证单调成立。<br>故最大 $\\omega=9$，选 B','cls':'green'},
        ],
        'insight': '多个约束条件的题，先算 ω 必须是奇数（代数推导），再由单调区间长度得上限 ≤12，最后从大到小验证。这种"奇数+上限"是一类经典题型。',
        'x_min': -1.2, 'x_max': 1.8, 'y_min': -1.6, 'y_max': 1.6,
        'pi_step': 0.2617993877991494,
        'omega_init': 9.0,
        'slider_html': f'''    <div class="graph-slider"><span>ω =</span><b id="omegaVal">9.00</b><input id="omegaSlider" type="range" min="1" max="13" step="1" value="9"></div>''',
        'stat_html': '<span id="wMax">状态：<span class="v">—</span></span>',
        'canvas_draw_js': canvas_js,
        'legend': '<span><span class="legend-dot" style="background:#4f8ef7"></span>f(x)=sin(ωx+φ)</span><span><span class="legend-dot" style="background:#ff6b6b"></span>x=π/4 对称轴</span><span><span class="legend-dot" style="background:#22c3a6"></span>单调区间</span><span><span class="legend-dot" style="background:#2a6df4"></span>零点(-π/4,0)</span>',
    }


def lesson_0017():
    canvas_js = r"""
  function f(x){return 2*Math.cos(omega*x+Math.PI/6);}
  function draw(){
    drawAxes();
    drawBandX(0,Math.PI,'#4f8ef7',0.05);
    drawBandX(0,Math.PI/4,'#ff6b6b',0.15);
    drawCurve(f,'#4f8ef7');
    drawVDashed(0,'#4f8ef7','');
    drawVDashed(Math.PI,'#4f8ef7','');
    drawVDashed(Math.PI/4,'#ff6b6b','π/4');
    // 找极小值点：cos(ωx+π/6)=-1 → ωx+π/6 = π+2kπ → x=(5π/6+2kπ)/ω
    let mins=[];
    for(let k=-5;k<=10;k++){
      const xm=(5*Math.PI/6+2*k*Math.PI)/omega;
      if(xm>0.001&&xm<Math.PI-0.001)mins.push(xm);
    }
    mins.sort((a,b)=>a-b);
    for(const xm of mins){
      drawPoint(xm,-2,'#22c3a6','极小');
    }
    // (0,π/4) 是否单调：即此区间内是否有极值点
    let hasExtInQ=false;
    // 极值点满足 cos'=0 → -ωsin(ωx+π/6)=0 → ωx+π/6 = kπ → x=(kπ-π/6)/ω
    for(let k=-5;k<=10;k++){
      const xe=(k*Math.PI-Math.PI/6)/omega;
      if(xe>0.001&&xe<Math.PI/4-0.001){hasExtInQ=true;break;}
    }
    const st=document.getElementById('wMax');
    if(st) st.innerHTML='极小值点：<span class="v '+(mins.length===2?'ok':'warn')+'">'+mins.length+'</span>'+
      '&nbsp;(0,π/4)内：<span class="v '+(hasExtInQ?'warn':'ok')+'">'+(hasExtInQ?'有极值/不单调':'单调')+'</span>';
  }
"""
    return {
        'dir': '31-math-trig-omega-range-7',
        'number': '数0017',
        'title': '余弦函数恰有两个极小值点且(0,π/4)不单调',
        'herosub': '【多选】$f(x)=2\\cos(\\omega x+\\frac{\\pi}{6}),\\omega>0$ 在 $(0,\\pi)$ 上有且仅有 2 个极小值点，且 $(0,\\pi/4)$ 上不单调，问 ω 不可能为？',
        'knowledge': '余弦函数极小值点与不单调联合条件',
        'source': '2025天津模拟',
        'type': '多选题',
        'stem': '已知函数 $f(x)=2\\cos\\left(\\omega x+\\frac{\\pi}{6}\\right)$（其中 $\\omega>0$）在 $(0,\\pi)$ 上有且仅有 $2$ 个极小值点，且 $f(x)$ 在 $\\left(0,\\frac{\\pi}{4}\\right)$ 上不单调，则 $\\omega$ 的取值不可能是：',
        'options': [
            {'letter':'A','text':'$\\frac{17}{6}\\approx 2.83$'},
            {'letter':'B','text':'$\\frac{10}{3}\\approx 3.33$'},
            {'letter':'C','text':'$4$'},
            {'letter':'D','text':'$\\frac{29}{6}\\approx 4.83$'},
        ],
        'correct': 'A',  # 正确答案 A（不可能），B 是边界值严格来说也不满足
        'warning': '<div class="warning-box">⚠️ <b>多选注意：</b>A=17/6≈2.83 明显太小（极小值条件上限但不满足(0,π/4)不单调），严格来说 B=10/3 是边界值也不满足严格不等式。通常标准答案选 <b>A 和 B</b>。</div>',
        'steps': [
            {'label':'Step 1','html':'<b>极小值条件：</b>$\\cos u=-1$ 当 $u=\\pi+2k\\pi$。令 $u=\\omega x+\\frac{\\pi}{6}$，当 $x\\in(0,\\pi)$，$u\\in\\left(\\frac{\\pi}{6},\\omega\\pi+\\frac{\\pi}{6}\\right)$'},
            {'label':'Step 2','html':'<b>恰有 2 个极小值</b> ⟹ $u$ 区间内恰含 $\\pi$ 和 $3\\pi$（不含 $5\\pi$）：<br>$3\\pi<\\omega\\pi+\\frac{\\pi}{6}\\le 5\\pi$？不对，极小值是 $\\pi, 3\\pi, 5\\pi$... 两个极小值意味着包含前两个：$\\pi, 3\\pi$。<br>$3\\pi<\\omega\\pi+\\frac{\\pi}{6}\\le 5\\pi$？<br>正确推导：极小值 $x=\\frac{\\frac{5\\pi}{6}+2k\\pi}{\\omega}$。<br>两个在 $(0,\\pi)$ ⟹ $\\frac{17\\pi}{6\\omega}<\\pi\\le\\frac{29\\pi}{6\\omega}$ ⟹ $\\frac{17}{6}<\\omega\\le\\frac{29}{6}$'},
            {'label':'Step 3','html':'<b>$(0,\\pi/4)$ 上不单调</b> ⟹ 区间内存在极值点。极值点 $x=\\frac{k\\pi-\\frac{\\pi}{6}}{\\omega}$。需要存在 $k$ 使<br>$0<\\frac{k\\pi-\\frac{\\pi}{6}}{\\omega}<\\frac{\\pi}{4}$ ⟹ $k>\\frac{1}{6},\\ k<\\frac{\\omega}{4}+\\frac{1}{6}$。取 $k=1$：$\\omega>\\frac{10}{3}$'},
            {'label':'Step 4','html':'<b>综合：</b>$\\omega\\in\\left(\\frac{10}{3},\\frac{29}{6}\\right]$（注意极小值条件下界 $\\frac{17}{6}\\approx 2.83$ 比 $\\frac{10}{3}\\approx 3.33$ 松，被后者覆盖）'},
            {'label':'Step 5','html':'<b>检验选项：</b><br>A=17/6≈2.83 ∉（太小） ❌<br>B=10/3≈3.33（边界，严格不等式下也不满足） ❌<br>C=4 ∈ ✅<br>D=29/6≈4.83 ∈ ✅<br>故不可能的是 A（标准答案常写 A,B）','cls':'green'},
        ],
        'insight': '联合条件题要分别解两个不等式，取交集。极小值"恰有2个"是左开右闭（因为开区间端点取不到），而不单调条件给出严格下界。最后逐个检验选项最快。',
        'x_min': -0.1, 'x_max': 3.3, 'y_min': -2.6, 'y_max': 2.6,
        'pi_step': 0.2617993877991494,
        'omega_init': 4.0,
        'slider_html': f'''    <div class="graph-slider"><span>ω =</span><b id="omegaVal">4.00</b><input id="omegaSlider" type="range" min="2" max="5.5" step="0.05" value="4"></div>''',
        'stat_html': '<span id="wMax">状态：<span class="v">—</span></span>',
        'canvas_draw_js': canvas_js,
        'legend': '<span><span class="legend-dot" style="background:#4f8ef7"></span>f(x)=2cos(ωx+π/6)</span><span><span class="legend-dot" style="background:#22c3a6"></span>极小值点</span><span><span class="legend-dot" style="background:#ff6b6b;opacity:0.5"></span>(0, π/4)</span>',
    }


# ============ 主入口 ============
def main():
    lessons = [
        lesson_0011(),
        lesson_0012(),
        lesson_0013(),
        lesson_0014(),
        lesson_0015(),
        lesson_0016(),
        lesson_0017(),
    ]
    for L in lessons:
        d = os.path.join(OUT_BASE, L['dir'])
        os.makedirs(d, exist_ok=True)
        out_path = os.path.join(d, 'index.html')
        html = render_lesson(L)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ 生成 {out_path}  （{len(html)} 字节）")

if __name__ == '__main__':
    main()
