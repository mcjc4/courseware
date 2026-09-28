/* =========================================================================
 * inter.js —— 单题课件「互动探究」段（模式 B 拖拽仿真 / 模式 A 分步动画）
 * -------------------------------------------------------------------------
 * 页面引入两行（顺序不能反）：
 *   <script src="../../inter/cfg-0926.js"></script>
 *   <script src="../../inter/inter.js"></script>
 * 引擎按当前页题号（目录前缀数字）取 window.MC_INTER_CFG[q] 配置，
 * 自建 <section id="mcInter"> 插到题目卡之后、命中分析段之前。
 * 配置契约：
 *   { mode:'sim', title, tip, note,
 *     view:{xr:[x0,x1], yr:[y0,y1], xt:[..], yt:[..]},
 *     params:[{key,label,min,max,step,val,fmt}],
 *     drag:{key,xr:[a,b]},                       // 画布水平拖拽手柄（改哪个参数）
 *     curves:[{expr:'Math.pow(x,p.a)', color, dash, domain:'x>0'}],
 *     readouts:[{label, expr:'p.a', fmt}],       // expr 用 (x,p) 或 (p) 求值
 *     judge:{expr:'p.a>0', ok:'…', bad:'…'} }
 *   { mode:'steps', title, tip, note,
 *     steps:[{tx:'步骤名', desc:'KaTeX 讲解', vals:{t:2.5}}],
 *     bars:[{key:'t', label:'t 的取值', min:0, max:5, fmt:'v=>v.toFixed(2)'}] }
 * ========================================================================= */
(function () {
  'use strict';
  var BASE = (function () {
    try { var c = document.currentScript; if (c && c.src) return c.src.replace(/[^\/]*$/, ''); } catch (e) {}
    return '../../inter/';
  })();

  function $(s, r) { return (r || document).querySelector(s); }
  function esc(s) { return String(s == null ? '' : s); }
  /* 保护 $...$ 数学段里的 < > 不被 HTML 解析器吃掉（tip/note 走 innerHTML） */
  function protectMath(html) {
    return String(html == null ? '' : html).replace(/\$\$[\s\S]*?\$\$|\$[^$\n]*?\$/g, function (m) {
      return m.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    });
  }
  function qNo() {
    var m = (location.pathname || '').match(/\/lessons\/(\d+)-/);
    if (m) return parseInt(m[1], 10);
    var mm = (document.querySelector('meta[name="number"]') || {}).content;
    return mm ? parseInt(mm, 10) : null;
  }
  function mk(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }
  function fnOf(expr, args) {
    return new Function(args.join(','), 'return (' + expr + ');');
  }
  function num(v, d) {
    if (typeof v === 'number') {
      if (!isFinite(v)) return '—';
      var s = v.toFixed(d == null ? 3 : d);
      return s.replace(/\.?0+$/, function (m) { return m.indexOf('.') === 0 ? '' : m; }) || s;
    }
    return String(v);
  }
  function renderMath(el) {
    if (el && window.renderMathInElement) {
      try {
        window.renderMathInElement(el, {
          delimiters: [{ left: '$$', right: '$$', display: true }, { left: '$', right: '$', display: false }],
          throwOnError: false, ignoredTags: ['textarea', 'script', 'noscript', 'style', 'pre']
        });
      } catch (e) {}
    }
  }
  function injectCss() {
    if ($('#mcInterCss')) return;
    var l = document.createElement('link');
    l.id = 'mcInterCss'; l.rel = 'stylesheet'; l.href = BASE + 'inter.css';
    (document.head || document.documentElement).appendChild(l);
  }

  /* ---------------------------------------------------------- 模式 B 仿真 */
  function buildSim(host, cfg) {
    var p = {};
    (cfg.params || []).forEach(function (d) { p[d.key] = d.val; });
    var view = cfg.view || { xr: [-4, 4], yr: [-4, 4] };
    var CW = 520, CH = 340, DPR = Math.min(2.5, window.devicePixelRatio || 1);

    var wrap = mk('div', 'it-cvwrap');
    var cv = mk('canvas');
    cv.width = CW; cv.height = CH;
    wrap.appendChild(cv);
    var side = mk('div', 'it-side');
    var stage = mk('div', 'it-stage');
    stage.appendChild(wrap); stage.appendChild(side);
    host.appendChild(stage);

    var ctx = cv.getContext('2d');
    var pad = { l: 40, r: 14, t: 14, b: 30 };

    function X(px) { return view.xr[0] + (px - pad.l) / (CW - pad.l - pad.r) * (view.xr[1] - view.xr[0]); }
    function xx(x) { return pad.l + (x - view.xr[0]) / (view.xr[1] - view.xr[0]) * (CW - pad.l - pad.r); }
    function yy(y) { return pad.t + (view.yr[1] - y) / (view.yr[1] - view.yr[0]) * (CH - pad.t - pad.b); }
    function fit() {
      var dis = cv.clientWidth || CW;
      var k = Math.min(2.6, Math.max(1, dis / CW));
      cv.width = Math.round(CW * k * DPR / 2) * 2;
      cv.height = Math.round(CH * k * DPR / 2) * 2;
      cv.style.height = (cv.height / (cv.width / (cv.clientWidth || CW))) + 'px';
      ctx.setTransform(cv.width / CW, 0, 0, cv.width / CW, 0, 0);
    }

    function grid() {
      ctx.clearRect(0, 0, CW, CH);
      ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, CW, CH);
      var x0 = Math.ceil(view.xr[0]), x1 = Math.floor(view.xr[1]), i;
      ctx.strokeStyle = 'rgba(37,99,235,.08)'; ctx.lineWidth = 1;
      ctx.fillStyle = '#9aa1ab'; ctx.font = '10px system-ui';
      for (i = x0; i <= x1; i++) {
        ctx.beginPath(); ctx.moveTo(xx(i), pad.t); ctx.lineTo(xx(i), CH - pad.b); ctx.stroke();
        if (i !== 0) { ctx.textAlign = 'center'; ctx.fillText(i, xx(i), CH - pad.b + 14); }
      }
      var y0 = Math.ceil(view.yr[0]), y1 = Math.floor(view.yr[1]);
      for (i = y0; i <= y1; i++) {
        ctx.beginPath(); ctx.moveTo(pad.l, yy(i)); ctx.lineTo(CW - pad.r, yy(i)); ctx.stroke();
        if (i !== 0) { ctx.textAlign = 'right'; ctx.fillText(i, pad.l - 6, yy(i) + 3); }
      }
      ctx.strokeStyle = '#9db9dd'; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.moveTo(pad.l, yy(0)); ctx.lineTo(CW - pad.r, yy(0)); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(xx(0), pad.t); ctx.lineTo(xx(0), CH - pad.b); ctx.stroke();
      ctx.textAlign = 'right'; ctx.fillStyle = '#5c6470';
      ctx.fillText('x', CW - pad.r, yy(0) - 5); ctx.fillText('y', xx(0) + 14, pad.t + 8);
    }

    function curves() {
      (cfg.curves || []).forEach(function (c) {
        /* 竖直参考线（如对称轴 x=2） */
        if (c.vline != null) {
          ctx.strokeStyle = c.color || '#b8720e';
          ctx.lineWidth = c.w || 1.2;
          ctx.setLineDash(c.dash === false ? [] : [5, 4]);
          ctx.beginPath();
          ctx.moveTo(xx(c.vline), pad.t); ctx.lineTo(xx(c.vline), CH - pad.b);
          ctx.stroke(); ctx.setLineDash([]);
          return;
        }
        var f;
        try { f = fnOf(c.expr, ['x', 'p']); } catch (e) { return; }
        ctx.strokeStyle = c.color || '#2563eb';
        ctx.lineWidth = c.w || 2;
        ctx.setLineDash(c.dash ? [5, 4] : []);
        ctx.beginPath();
        var started = false;
        var PW = CW - pad.l - pad.r;
      for (var pi = 0; pi <= PW; pi++) {
          var x = X(pad.l + pi);
          if (c.domain && !fnOf(c.domain, ['x', 'p'])(x, p)) { started = false; continue; }
          var y;
          try { y = f(x, p); } catch (e) { started = false; continue; }
          if (!isFinite(y)) { started = false; continue; }
          var py = yy(y);
          if (py < pad.t - 60 || py > CH - pad.b + 60) { started = false; continue; }
          if (!started) { ctx.moveTo(xx(x), py); started = true; } else ctx.lineTo(xx(x), py);
        }
        ctx.stroke(); ctx.setLineDash([]);
      });
    }

    var dg = cfg.drag;
    function handlePos() {
      if (!dg) return null;
      var d0 = (cfg.params || []).filter(function (d) { return d.key === dg.key; })[0];
      if (!d0) return null;
      var t = (p[dg.key] - d0.min) / (d0.max - d0.min);
      var gx = xx(dg.xr[0] + t * (dg.xr[1] - dg.xr[0]));
      return { x: gx, y: yy(dg.y == null ? view.yr[1] * 0.62 : dg.y) };
    }
    function handle() {
      var h = handlePos(); if (!h) return;
      ctx.beginPath(); ctx.arc(h.x, h.y, 7, 0, Math.PI * 2);
      ctx.fillStyle = '#2563eb'; ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.stroke();
      ctx.font = '600 11px system-ui'; ctx.fillStyle = '#2563eb'; ctx.textAlign = 'center';
      ctx.fillText('⇔拖我', h.x, h.y - 12);
    }

    /* 自定义绘制钩子：cfg.custom(ctx, p, U)，U 提供坐标变换与视图 */
    var U = { view: view, pad: pad, CW: CW, CH: CH, x: X, xx: xx, yy: yy, p: null };
    function custom() {
      if (typeof cfg.custom !== 'function') return;
      try { cfg.custom(ctx, p, U); } catch (e) {}
    }
    function draw() { grid(); curves(); custom(); handle(); }

    function paintSide() {
      var read = $('.it-read', side);
      if (read) {
        var h = '';
        (cfg.readouts || []).forEach(function (r) {
          var v;
          try { v = fnOf(r.expr, ['p', 'num'])(p, num); } catch (e) { v = '—'; }
          if (typeof v === 'number' && r.fmt !== 'raw') v = num(v, r.d == null ? 3 : r.d);
          h += '<div class="rw"><span>' + esc(r.label) + '</span><b>' + esc(v) + '</b></div>';
        });
        read.innerHTML = h;
      }
      var jd = $('.it-judge', side);
      if (jd && cfg.judge) {
        var ok = false;
        try { ok = !!fnOf(cfg.judge.expr, ['p'])(p); } catch (e) {}
        jd.className = 'it-judge ' + (cfg.judge.tri ? (ok ? cfg.judge.clsOk || 'ok' : cfg.judge.clsBad || 'bad') : (ok ? 'ok' : 'warn'));
        jd.innerHTML = esc(ok ? cfg.judge.ok : cfg.judge.bad);
      }
      (cfg.params || []).forEach(function (d) {
        var el = $('[data-pv="' + d.key + '"]', side);
        if (el) el.textContent = num(p[d.key], d.d == null ? 2 : d.d);
        var sl = $('[data-sl="' + d.key + '"]', side);
        if (sl && sl.value != p[d.key]) sl.value = p[d.key];
      });
    }

    /* 参数滑块 */
    (cfg.params || []).forEach(function (d) {
      var box = mk('div', 'it-sl');
      box.innerHTML = '<div class="lb"><span>' + esc(d.label) + '</span><b data-pv="' + d.key + '">' +
        num(p[d.key], d.d == null ? 2 : d.d) + '</b></div>' +
        '<input type="range" data-sl="' + d.key + '" min="' + d.min + '" max="' + d.max + '" step="' + d.step + '" value="' + p[d.key] + '">';
      side.appendChild(box);
      $('input', box).addEventListener('input', function () {
        p[d.key] = parseFloat(this.value); draw(); paintSide();
      });
    });
    side.appendChild(mk('div', 'it-read'));
    if (cfg.judge) side.appendChild(mk('div', 'it-judge'));

    /* 画布拖拽 */
    if (dg) {
      var dragging = false;
      function toVal(px) {
        var d0 = (cfg.params || []).filter(function (d) { return d.key === dg.key; })[0];
        var t = (px - xx(dg.xr[0])) / (xx(dg.xr[1]) - xx(dg.xr[0]));
        t = Math.max(0, Math.min(1, t));
        var v = d0.min + t * (d0.max - d0.min);
        /* snap: 吸附到关键值（如 π/3 的整数倍），GeoGebra 风格手感 */
        if (d0.snap) v = Math.round(v / d0.snap) * d0.snap;
        else v = Math.round(v / d0.step) * d0.step;
        return Math.max(d0.min, Math.min(d0.max, v));
      }
      function pxOf(e) {
        var r = cv.getBoundingClientRect();
        return (e.clientX - r.left) / r.width * CW;
      }
      cv.addEventListener('pointerdown', function (e) {
        var h = handlePos(); if (!h) return;
        var mx = pxOf(e), my = (e.clientY - cv.getBoundingClientRect().top) / cv.getBoundingClientRect().height * CH;
        if (Math.abs(mx - h.x) < 22 && Math.abs(my - h.y) < 26) {
          dragging = true; cv.setPointerCapture(e.pointerId); e.preventDefault();
        }
      });
      cv.addEventListener('pointermove', function (e) {
        if (!dragging) return;
        p[dg.key] = toVal(pxOf(e)); draw(); paintSide();
      });
      cv.addEventListener('pointerup', function () { dragging = false; });
      cv.addEventListener('pointercancel', function () { dragging = false; });
    }

    fit(); draw(); paintSide();
    window.addEventListener('resize', function () { fit(); draw(); });
    /* 挂载瞬间容器宽度可能尚未稳定，布局落定后再校准一次分辨率 */
    [80, 400].forEach(function (ms) { setTimeout(function () { fit(); draw(); }, ms); });
    window.addEventListener('load', function () { fit(); draw(); });
  }

  /* ------------------------------------------------------ 模式 A 分步动画 */
  function buildSteps(host, cfg) {
    var steps = cfg.steps || [];
    var cur = 0, playing = false, sp = 1, raf = null;
    var vals = {};
    function ease(t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }

    var chips = mk('div', 'it-chips');
    steps.forEach(function (s, i) {
      var b = mk('button', '', esc(s.tx));
      b.addEventListener('click', function () { go(i, true); });
      chips.appendChild(b);
    });
    host.appendChild(chips);

    var ctrl = mk('div', 'it-ctrl');
    ctrl.innerHTML = '<button data-a="prev" title="上一步">◀</button>' +
      '<button data-a="play" title="播放/暂停">▶</button>' +
      '<button data-a="next" title="下一步">▶</button>' +
      '<button data-a="reset" title="重置">↺</button>' +
      '<span class="sp">速度<input type="range" data-a="sp" min="0.5" max="2" step="0.1" value="1"></span>';
    host.appendChild(ctrl);

    var barsBox = null;
    if (cfg.bars && cfg.bars.length) {
      barsBox = mk('div', 'it-bars');
      cfg.bars.forEach(function (b) {
        barsBox.appendChild(mk('div', 'it-bar',
          '<div class="t"><span>' + esc(b.label) + '</span><b data-bv="' + b.key + '">—</b></div>' +
          '<div class="tr"><div class="fl" data-bf="' + b.key + '"></div></div>'));
      });
      host.appendChild(barsBox);
    }
    var desc = mk('div', 'it-desc');
    host.appendChild(desc);

    function paintBars(v) {
      if (!barsBox) return;
      (cfg.bars || []).forEach(function (b) {
        var val = v[b.key];
        var el = $('[data-bv="' + b.key + '"]', barsBox);
        var fl = $('[data-bf="' + b.key + '"]', barsBox);
        if (el) el.textContent = (typeof val === 'number') ? num(val, b.d == null ? 2 : b.d) : esc(val);
        if (fl && typeof val === 'number') {
          var t = (val - b.min) / (b.max - b.min);
          fl.style.width = (Math.max(0, Math.min(1, t)) * 100) + '%';
        }
      });
    }
    function paintChips() {
      [].forEach.call(chips.children, function (b, i) {
        b.className = i === cur ? 'on' : (i < cur ? 'done' : '');
      });
    }
    function paint() {
      var s = steps[cur];
      desc.innerHTML = '<span class="stepno">第 ' + (cur + 1) + '/' + steps.length + ' 步</span>' + (s ? s.desc : '');
      renderMath(desc);
      paintChips();
      paintBars(s ? (s.vals || {}) : {});
    }
    function go(i, stop) {
      if (stop) { playing = false; }
      cur = Math.max(0, Math.min(steps.length - 1, i));
      var from = Object.assign({}, vals);
      var to = steps[cur].vals || {};
      var t0 = performance.now(), dur = 620 / sp;
      if (raf) cancelAnimationFrame(raf);
      function tick(now) {
        var t = Math.min(1, (now - t0) / dur), e = ease(t);
        vals = {};
        Object.keys(to).forEach(function (k) {
          vals[k] = (typeof to[k] === 'number' && typeof from[k] === 'number')
            ? from[k] + (to[k] - from[k]) * e : to[k];
        });
        paintBars(vals);
        if (t < 1) raf = requestAnimationFrame(tick);
        else { vals = Object.assign({}, to); paintBars(vals); }
      }
      paint();
      raf = requestAnimationFrame(tick);
    }
    function next() { if (cur < steps.length - 1) go(cur + 1); else { playing = false; } }
    ctrl.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-a]'); if (!b) return;
      var a = b.getAttribute('data-a');
      if (a === 'prev') { playing = false; go(cur - 1); }
      else if (a === 'next') { playing = false; next(); }
      else if (a === 'reset') { playing = false; vals = {}; go(0, true); }
      else if (a === 'play') {
        playing = !playing;
        b.textContent = playing ? '⏸' : '▶';
        if (playing) {
          if (cur >= steps.length - 1) { cur = 0; vals = {}; }
          (function loop() {
            if (!playing) return;
            go(cur, false);
            setTimeout(function () {
              if (!playing) return;
              if (cur < steps.length - 1) { cur++; loop(); }
              else { playing = false; var pb = $('[data-a="play"]', ctrl); if (pb) pb.textContent = '▶'; }
            }, 1500 / sp);
          })();
        }
      }
    });
    $('[data-a="sp"]', ctrl).addEventListener('input', function () { sp = parseFloat(this.value); });
    vals = Object.assign({}, (steps[0] || {}).vals || {});
    go(0, true);
  }

  /* ------------------------------------------------------------- 挂载 */
  function mount(cfg) {
    if (document.getElementById('mcInter')) return;
    injectCss();
    var sec = mk('section', 'card');
    sec.id = 'mcInter';
    var h = mk('h2');
    h.innerHTML = '<span class="dot"></span>' + (cfg.mode === 'sim' ? '🧭 互动探究 · 拖动看变化' : '🎬 分步动画 · 跟着走一遍');
    sec.appendChild(h);
    if (cfg.tip) sec.appendChild(mk('div', 'it-sum', protectMath(cfg.tip)));
    if (cfg.title) sec.appendChild(mk('div', 'it-sum', '<b>' + protectMath(cfg.title) + '</b>'));
    var body = mk('div');
    sec.appendChild(body);
    if (cfg.note) sec.appendChild(mk('div', 'it-hint', protectMath(cfg.note)));

    var anchor = null;
    var mf = document.getElementById('mcFitCard');
    if (mf) anchor = { before: mf };
    var qc = document.querySelectorAll('section.qcard');
    if (!anchor && qc.length) anchor = { after: qc[qc.length - 1] };
    if (anchor && anchor.before) anchor.before.parentNode.insertBefore(sec, anchor.before);
    else if (anchor && anchor.after) anchor.after.parentNode.insertBefore(sec, anchor.after.nextSibling);
    else {
      var c = $('.container') || document.body;
      c.appendChild(sec);
    }
    try {
      if (cfg.mode === 'sim') buildSim(body, cfg); else buildSteps(body, cfg);
      renderMath(sec);
    } catch (e) {
      body.appendChild(mk('div', 'it-hint', '互动段初始化失败：' + e.message));
    }
  }

  function boot() {
    var n = qNo();
    var cfg = (window.MC_INTER_CFG || {})[n];
    if (!cfg) return;
    mount(cfg);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
