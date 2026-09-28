/* =========================================================================
 * cfg-0926.js —— 0926 数学错题批（lesson 87~101）互动段配置
 * 键 = 课件题号（目录前缀数字），与 lessons 目录下同名编号的 index.html 一一对应
 * ========================================================================= */
window.MC_INTER_CFG = window.MC_INTER_CFG || {};

/* ---------------- 87 · 幂函数单调性与充要条件（模式 B 拖拽） ---------------- */
window.MC_INTER_CFG[87] = {
  mode: 'sim',
  title: '拖动 α，看 $f(x)=x^{\\alpha}$ 在 $(0,+\\infty)$ 上的单调性怎么变',
  tip: '抓住一件事：<b>幂函数在 $(0,+\\infty)$ 上的单调性完全由 α 的符号决定</b>——$\\alpha>0$ 递增、$\\alpha<0$ 递减、$\\alpha=0$ 恒为 1。拖到 α 穿过 0 的那一下，就是本题「充分性 + 必要性」双向成立的证据。',
  view: { xr: [0.2, 3], yr: [-1.5, 4] },
  params: [{ key: 'a', label: '指数 α', min: -3, max: 3, step: 0.25, val: -1, d: 2 }],
  drag: { key: 'a', xr: [0.4, 2.8], y: 3.2 },
  curves: [
    { expr: 'Math.pow(x,p.a)', color: '#2563eb', domain: 'x>0', w: 2.2 },
    { expr: 'x', color: '#9aa1ab', dash: true, w: 1.2 },
    { expr: '1', color: '#b8720e', dash: true, w: 1.2 }
  ],
  readouts: [
    { label: 'α 取值', expr: 'p.a', d: 2 },
    { label: '在 (0,+∞) 单调性', expr: 'p.a>0?"递增 ↑":(p.a<0?"递减 ↓":"常数 1")', fmt: 'raw' },
    { label: 'α<0 是否成立', expr: 'p.a<0?"是":"否"', fmt: 'raw' }
  ],
  judge: {
    expr: 'p.a<0',
    ok: '✓ α<0 → 递减：充分性成立',
    bad: '✗ α≥0 → 不递减：递减必 α<0，必要性也成立'
  },
  note: '本题答案 C（充要条件）。常见错误是只记「α<0 图象下降」就选 A——忘了反过来「递减 ⇒ α<0」同样成立。'
};

/* ---------------- 91 · 指数函数换元最值与分离参数（模式 A 分步动画） ---------------- */
window.MC_INTER_CFG[91] = {
  mode: 'steps',
  title: '跟着走一遍：换元 $t=2^{x}\\ (t>0)$ → 配方求 $k$ → 分离参数求 $a$',
  tip: '两步都卡在同一个地方：<b>换元后新变量 t 有隐含范围 $t>0$</b>。$k$ 的取舍靠顶点是否在 $t>0$ 内，$a$ 的上界靠「有解」转「最大值」。',
  bars: [
    { key: 't', label: '换元变量 $t=2^{x}$', min: 0, max: 5, d: 2 },
    { key: 'k', label: '参数 $k$', min: -3, max: 3, d: 2 },
    { key: 'mn', label: '$f(x)$ 最小值', min: -4, max: 2, d: 2 },
    { key: 'a', label: '参数上界 $a$', min: 0, max: 1, d: 3 }
  ],
  steps: [
    {
      tx: '① 换元',
      vals: { t: 1, k: 0, mn: 1, a: 0 },
      desc: '令 $t=2^{x}$，则 $t>0$（<b>这是最容易漏的隐含范围</b>），$2^{2x}=t^{2}$，于是 $f(x)=t^{2}+2kt+1$ 化为关于 $t$ 的二次函数 $g(t)=t^{2}+2kt+1\\ (t>0)$。'
    },
    {
      tx: '② 配方求 k',
      vals: { t: 2, k: -2, mn: -3, a: 0 },
      desc: '$g(t)=(t+k)^{2}+1-k^{2}$。要在 $t>0$ 上取到最小值 $-3$，必须顶点 $t=-k>0$（即 $k<0$，<b>否则最小值在 $t\\to0^{+}$ 处取不到</b>），此时 $1-k^{2}=-3\\Rightarrow k^{2}=4$。结合 $k<0$ 得 $k=-2$。'
    },
    {
      tx: '③ 分离参数',
      vals: { t: 3, k: -2, mn: -3, a: 0.5 },
      desc: '第二问 $f(x)\\le \\dfrac{2^{x}}{a}-8$ 有实数解：先由 $\\dfrac{2^{x}}{a}$ 有意义知 $a>0$。代入 $t$：$t^{2}-4t+1\\le \\dfrac{t}{a}-8$，整理为 $a\\le \\dfrac{t}{t^{2}-4t+9}$（$t>0$）。「有解」⇔ $a$ 不超过右式的<b>最大值</b>：由 $t^{2}-4t+9=(t-2)^{2}+5$ 且 $\\dfrac{t}{t^{2}-4t+9}$ 在 $t=3$ 处取最大 $\\dfrac{1}{2}$，故 $a\\le\\dfrac{1}{2}$。'
    },
    {
      tx: '④ 定稿',
      vals: { t: 3, k: -2, mn: -3, a: 0.5 },
      desc: '答案：(1) $k=-2$；(2) $0<a\\le\\dfrac{1}{2}$。回头检查端点：$a=\\dfrac{1}{2}$ 时 $t=3$（即 $x=\\log_{2}3$）等号成立，端点<b>闭合</b>，不能写成 $a<\\dfrac{1}{2}$。'
    }
  ],
  note: '两处易错：① 换元后忘记 $t>0$，导致 $k$ 多出一个正数解；② 分离参数后把「有解」当成「恒成立」，方向搞反。'
};

/* ---------------- 88 · 幂函数图象识别（模式 B 拖拽） ---------------- */
window.MC_INTER_CFG[88] = {
  mode: 'sim',
  title: '拖动 α，看图象形状、与 $y=x$ 的相对位置、奇偶对称怎么同时变化',
  tip: '本题的四个条件是<b>四个可验证的图象特征</b>：过原点（α>0）、关于 y 轴对称（α 使 $f$ 为偶函数）、$(0,+\\infty)$ 上递增（α>0）、$0<x<1$ 时在 $y=x$ <b>上方</b>（α<1）。拖 α 让四条同时成立，就是答案。',
  view: { xr: [-2, 2.2], yr: [-1.4, 3.4] },
  params: [{ key: 'a', label: '指数 α', min: -3, max: 3, step: 0.25, val: 2, d: 2 }],
  drag: { key: 'a', xr: [1.3, 2.1], y: 2.8 },
  curves: [
    { expr: 'Math.pow(x,p.a)', color: '#2563eb', domain: 'x>0', w: 2.2 },
    { expr: 'Math.pow(-x,p.a)', color: '#93b4f7', domain: 'x<0', dash: true, w: 1.8 },
    { expr: 'x', color: '#9aa1ab', dash: true, w: 1.2 }
  ],
  readouts: [
    { label: 'α 取值', expr: 'p.a', d: 2 },
    { label: '0<x<1 与 y=x 相比', expr: '(p.a<1)?"在上方 ↑":"在下方 ↓"', fmt: 'raw' },
    { label: '(0,+∞) 单调性', expr: 'p.a>0?"递增 ↑":"递减 ↓"', fmt: 'raw' },
    { label: '是否过原点', expr: '(p.a>0)?"过":"不过"', fmt: 'raw' }
  ],
  judge: {
    expr: 'p.a>0&&p.a<1',
    ok: '✓ 四条件齐了：过原点 + 递增 + 上方 + 偶函数 ⇒ 形如 $x^{\\frac{2}{3}}$',
    bad: '✗ 拖到 0<α<1：既过原点又在 y=x 上方（α>1 会在下方，α<0 不过原点）'
  },
  note: '判别口诀：<b>α>0 过原点、α 越大（x>1 时）越陡、0<α<1 时被 y=x 压低反而在 x<1 处更高</b>。答案 B（$x^{\\frac{2}{3}}$ 型）。'
};

/* ---------------- 89 · 二次函数定区间最值（模式 B 拖拽） ---------------- */
window.MC_INTER_CFG[89] = {
  mode: 'sim',
  title: '拖动区间右端 $b$（左端用滑块），看 $g(x)=3x^{2}-12x+13$ 在 $[a,b]$ 上的最值怎么跳变',
  tip: '本题第 (1) 问解出 $a=3,\\ b=12$ 后，$g(x)=3x^{2}-12x+13$（对称轴 $x=2$，顶点 $(2,1)$）。<b>第二问的「不单调」就是区间跨住对称轴</b>——拖住两端让 $x=2$ 落在区间内部试试。',
  view: { xr: [-1, 5], yr: [-1, 6] },
  params: [
    { key: 'a', label: '区间左端 a', min: -1, max: 4, step: 0.1, val: 1.5, d: 1 },
    { key: 'b', label: '区间右端 b', min: -1, max: 5, step: 0.1, val: 2.5, d: 1 }
  ],
  drag: { key: 'b', xr: [0, 5], y: 5.2 },
  curves: [
    { expr: '3*x*x-12*x+13', color: '#2563eb', w: 2.2 },
    { vline: 2, color: '#b8720e' }
  ],
  custom: function (ctx, p, U) {
    /* 高亮 [a,b] 区间内的曲线段 */
    var lo = Math.min(p.a, p.b), hi = Math.max(p.a, p.b);
    ctx.strokeStyle = '#dc2626'; ctx.lineWidth = 3.4;
    ctx.beginPath();
    for (var i = 0; i <= 60; i++) {
      var x = lo + (hi - lo) * i / 60, y = 3 * x * x - 12 * x + 13;
      if (i === 0) ctx.moveTo(U.xx(x), U.yy(y)); else ctx.lineTo(U.xx(x), U.yy(y));
    }
    ctx.stroke();
    /* 区间端点的竖标线 */
    [lo, hi].forEach(function (x) {
      ctx.strokeStyle = 'rgba(220,38,38,.45)'; ctx.lineWidth = 1.2; ctx.setLineDash([4, 4]);
      ctx.beginPath(); ctx.moveTo(U.xx(x), U.yy(0)); ctx.lineTo(U.xx(x), U.yy(3 * x * x - 12 * x + 13)); ctx.stroke();
      ctx.setLineDash([]);
    });
  },
  readouts: [
    { label: '对称轴 x=2 在区间内', expr: '(Math.min(p.a,p.b)<2&&Math.max(p.a,p.b)>2)?"是 → 不单调":"否"', fmt: 'raw' },
    { label: '最小值', expr: '(Math.min(p.a,p.b)<2&&Math.max(p.a,p.b)>2)?1:Math.min(3*p.a*p.a-12*p.a+13,3*p.b*p.b-12*p.b+13)', d: 2 },
    { label: '最大值', expr: 'Math.max(3*p.a*p.a-12*p.a+13,3*p.b*p.b-12*p.b+13)', d: 2 }
  ],
  judge: {
    expr: 'Math.min(p.a,p.b)<2&&Math.max(p.a,p.b)>2',
    tri: true, clsOk: 'ok', clsBad: 'warn',
    ok: '✓ 区间跨住对称轴 x=2 ⇒ 在 (a,b) 上不单调',
    bad: '✗ 对称轴在区间外 ⇒ 在 (a,b) 上单调（左端 a<2<b 时才是本题要的「不单调」）'
  },
  note: '第 (2) 问的答案 $1<m<3$ 正是「区间 $(m-1,2m)$ 必须夹住 $x=2$」：$m-1<2<2m$。注意端点<b>开区间</b>不取等。'
};

/* ---------------- 90 · 幂函数偶函数单调与不等式（模式 B 拖拽） ---------------- */
window.MC_INTER_CFG[90] = {
  mode: 'sim',
  title: '拖动指数 $-n$，看「偶函数 + $(0,+\\infty)$ 递减」这两个条件如何锁死指数',
  tip: '条件有两把锁：<b>①偶函数</b>（图象关于 y 轴对称，α 的分母为偶数时成立）<b>②$(0,+\\infty)$ 递减</b>（α<0）。本题 $m=1$ 使指数 $=m^{2}-2m-3=-4$，正好同时满足。',
  view: { xr: [-2.2, 2.2], yr: [-1, 4.6] },
  params: [{ key: 'n', label: '指数 -n（n 为正整数）', min: 1, max: 4, step: 1, val: 4, d: 0 }],
  drag: { key: 'n', xr: [-1.8, 1.8], y: 4.0 },
  curves: [
    { expr: 'Math.pow(Math.abs(x),-p.n)', color: '#2563eb', w: 2.2 },
    { vline: 0, color: '#b8720e' }
  ],
  readouts: [
    { label: '指数 α', expr: '-p.n', d: 0 },
    { label: '在 (0,+∞)', expr: '"递减 ↓"', fmt: 'raw' },
    { label: '在 (-∞,0)', expr: '"递增 ↑"', fmt: 'raw' },
    { label: '奇偶性', expr: '(p.n%2===0)?"偶函数（关于 y 轴对称）":"奇函数（关于原点对称）"', fmt: 'raw' }
  ],
  judge: {
    expr: 'p.n%2===0',
    ok: '✓ n 为偶数 ⇒ 偶函数，图象关于 y 轴对称（本题 n=4）',
    bad: '✗ n 为奇数 ⇒ 奇函数，图象关于原点对称，不满足「偶函数」'
  },
  note: '第 (2) 问用「偶函数 + $(0,+\\infty)$ 递减」把不等式化成 $|2a+1|>|3-2a|$，解得 $a\\in(-\\infty,-\\frac12)\\cup(\\frac12,\\frac32)$——<b>偶函数的作用就是去掉负号讨论</b>。'
};

/* ---------------- 95 · 指数函数图象与渐近线（模式 B 拖拽） ---------------- */
window.MC_INTER_CFG[95] = {
  mode: 'sim',
  title: '拖动 $b$ 和 $a$，让图象同时满足「过原点」与「无限接近 $y=2$」',
  tip: '把两个条件翻译成式子：<b>过原点 ⇒ $a+b=0$</b>（因为 $|0|=0$ 时指数为 1）；<b>无限接近 $y=2$ ⇒ 水平渐近线 $y=b=2$</b>（因为 $|x|\\to\\infty$ 时 $a(\\frac12)^{|x|}\\to 0$）。两条一起定出 $a=-2,\\ b=2,\\ ab=-4$。',
  view: { xr: [-4, 4], yr: [-0.6, 3.6] },
  params: [
    { key: 'a', label: '系数 a', min: -4, max: 4, step: 0.25, val: -2, d: 2 },
    { key: 'b', label: '平移量 b（渐近线 y=b）', min: -2, max: 4, step: 0.25, val: 2, d: 2 }
  ],
  drag: { key: 'b', xr: [-3, 3], y: 3.3 },
  curves: [
    { expr: 'p.a*Math.pow(0.5,Math.abs(x))+p.b', color: '#2563eb', w: 2.2 },
    { expr: 'p.b', color: '#b8720e', dash: true, w: 1.4 }
  ],
  readouts: [
    { label: 'a + b（过原点需 =0）', expr: 'p.a+p.b', d: 2 },
    { label: '渐近线 y =', expr: 'p.b', d: 2 },
    { label: '是否过原点', expr: '(Math.abs(p.a+p.b)<0.06)?"过 ✓":"不过 ✗"', fmt: 'raw' },
    { label: 'a·b', expr: 'p.a*p.b', d: 2 }
  ],
  judge: {
    expr: 'Math.abs(p.a+p.b)<0.06&&Math.abs(p.b-2)<0.06',
    ok: '✓ 同时满足：过原点 + 渐近线 y=2 ⇒ $ab=-4$',
    bad: '✗ 还没同时满足：过原点要 $a+b=0$，渐近线要 $b=2$'
  },
  note: '注意 $y=a(\\frac12)^{|x|}+b$ 是<b>偶函数</b>（含 $|x|$），图象关于 y 轴对称；渐近线由上/下方趋近要看 $a$ 的正负——本题 $a=-2<0$，图象在 $y=2$ <b>下方</b>。'
};

/* ---------------- 96 · 解三角形角平分线（模式 B 拖拽） ---------------- */
window.MC_INTER_CFG[96] = {
  mode: 'sim',
  title: '拖动顶点 $A$ 的张口，看角平分线 $AD$ 与两侧面积比怎么变',
  tip: '角平分线把面积一分为二两个三角形，却<b>不</b>把面积平分：$\\dfrac{S_{\\triangle ABD}}{S_{\\triangle ACD}}=\\dfrac{BD}{CD}=\\dfrac{c}{b}$（角平分线定理）。<b>等面积法</b>是算 $AD$ 的快捷路径：$\\frac12 bc\\sin A=\\frac12 AD(b+c)\\sin\\frac{A}{2}$。',
  view: { xr: [-1.2, 6], yr: [-0.8, 5.4] },
  params: [
    { key: 'A', label: '∠A（度）', min: 20, max: 150, step: 1, val: 90, d: 0 },
    { key: 'c', label: '边 c = AB', min: 1, max: 5, step: 0.25, val: 3, d: 2 },
    { key: 'b', label: '边 b = AC', min: 1, max: 5, step: 0.25, val: 4, d: 2 }
  ],
  drag: { key: 'A', xr: [2.6, 5.6], y: 2.9 },
  curves: [],
  custom: function (ctx, p, U) {
    var A = p.A * Math.PI / 180, B = { x: 0, y: 0 };
    /* 以 A 为原点：AB 沿 +x 轴，AC 与 AB 夹角 A */
    var C = { x: p.b * Math.cos(A), y: p.b * Math.sin(A) };
    var Bp = { x: p.c, y: 0 };
    /* 角平分线方向（单位向量之和） */
    var d1 = { x: 1, y: 0 }, d2 = { x: Math.cos(A), y: Math.sin(A) };
    var dl = Math.sqrt((d1.x + d2.x) * (d1.x + d2.x) + (d1.y + d2.y) * (d1.y + d2.y)) || 1;
    var dir = { x: (d1.x + d2.x) / dl, y: (d1.y + d2.y) / dl };
    /* 角平分线与 BC 的交点 D（用角平分线定理定比例） */
    var tD = p.c / (p.b + p.c);
    var D = { x: Bp.x + (C.x - Bp.x) * tD, y: Bp.y + (C.y - Bp.y) * tD };
    function seg(a, b, color, w, dash) {
      ctx.strokeStyle = color; ctx.lineWidth = w || 1.8; ctx.setLineDash(dash || []);
      ctx.beginPath(); ctx.moveTo(U.xx(a.x), U.yy(a.y)); ctx.lineTo(U.xx(b.x), U.yy(b.y)); ctx.stroke();
      ctx.setLineDash([]);
    }
    /* 三个顶点 */
    [[B, 'B'], [C, 'C'], [Bp, 'B2']].forEach(function (v) {});
    seg(B, C, '#1f2430', 2);
    seg(B, Bp, '#1f2430', 2);
    seg(Bp, C, '#1f2430', 2);
    seg(B, D, '#dc2626', 2.6);
    /* 顶点标注 */
    ctx.fillStyle = '#1f2430'; ctx.font = '600 12px system-ui'; ctx.textAlign = 'center';
    ctx.fillText('A', U.xx(B.x) - 12, U.yy(B.y) + 4);
    ctx.fillText('B', U.xx(Bp.x) + 4, U.yy(Bp.y) + 14);
    ctx.fillText('C', U.xx(C.x), U.yy(C.y) - 8);
    ctx.fillStyle = '#dc2626';
    ctx.fillText('D', U.xx(D.x) + 2, U.yy(D.y) + 15);
    /* 顶点圆点 */
    [[B, '#1f2430'], [Bp, '#1f2430'], [C, '#1f2430'], [D, '#dc2626']].forEach(function (v) {
      ctx.beginPath(); ctx.arc(U.xx(v[0].x), U.yy(v[0].y), 4, 0, Math.PI * 2);
      ctx.fillStyle = v[1]; ctx.fill();
    });
  },
  readouts: [
    { label: '角平分线 AD 长', expr: '2*p.b*p.c*Math.cos(p.A*Math.PI/360)/(p.b+p.c)', d: 3 },
    { label: 'S△ABD : S△ACD', expr: 'num(p.c)+" : "+num(p.b)', fmt: 'raw' },
    { label: 'BD : CD', expr: 'num(p.c)+" : "+num(p.b)', fmt: 'raw' }
  ],
  judge: {
    expr: 'true', tri: true, clsOk: 'warn', clsBad: 'warn',
    ok: '角平分线定理：BD:CD = AB:AC = c:b，与 ∠A 无关——拖 ∠A 只改变 AD 的长短',
    bad: ''
  },
  note: '本题 $c=3$、$AD=1$、$\\cos A=-\\frac79$（钝角）。用等面积法 $\\frac12\\cdot b\\cdot 3\\cdot\\sin A=\\frac12\\cdot 1\\cdot(b+3)\\sin\\frac{A}{2}$ 先解出 $b$，再由余弦定理求 $a$，最后落在 $\\cos B=\\frac{2\\sqrt2}{3}$。'
};

/* ---------------- 98 · 分段函数单调性（模式 B 拖拽） ---------------- */
window.MC_INTER_CFG[98] = {
  mode: 'sim',
  title: '拖动 $a$，同时盯住三件事：左段递增、右段递增、衔接处不掉头',
  tip: '分段函数在 $\\mathbb R$ 上递增要<b>三个条件同时成立</b>：①左段 $(-\\infty,0)$ 递增（开口向下 ⇒ $a\\le0$）②右段 $[0,+\\infty)$ 递增（$e^{x}+a\\ge0$ 恒成立 ⇒ $a\\ge-1$）③接缝处不回落（$f(0^-)\\le f(0^+)$）。三条一起得 $a\\in[-1,0]$。',
  view: { xr: [-2.4, 2.4], yr: [-1.6, 3.2] },
  params: [{ key: 'a', label: '参数 a', min: -2, max: 1, step: 0.1, val: -1, d: 2 }],
  drag: { key: 'a', xr: [-2, 2], y: 2.9 },
  curves: [
    { expr: '(x<0)?(p.a*x*x+x+p.a):(Math.exp(x)+p.a*(x+1))', color: '#2563eb', w: 2.4 },
    { vline: 0, color: '#b8720e' }
  ],
  readouts: [
    { label: '①左段 (-∞,0) 递增', expr: '(p.a<=0)?"✓ 成立":"✗ 开口向上，先减后增"', fmt: 'raw' },
    { label: '②右段 [0,+∞) 递增', expr: '(p.a>=-1)?"✓ 成立":"✗ e^x+a 会变负"', fmt: 'raw' },
    { label: '③接缝 f(0⁻) ≤ f(0⁺)', expr: 'num(p.a)+" ≤ "+num(1+p.a)+(p.a<=1+p.a?" ✓":" ✗")', fmt: 'raw' }
  ],
  judge: {
    expr: 'p.a>=-1&&p.a<=0',
    ok: '✓ 三条件齐 ⇒ 在 R 上递增：$a\\in[-1,0]$',
    bad: '✗ 未同时满足①②③，拖动 a 找同时成立的位置'
  },
  note: '③ 这条最容易被忽略：即使两段各自递增，接缝处左段值仍可能大于右段值（$a>0$ 时会发生），整体就不递增了。'
};

/* ---------------- 101 · 三角函数平移对称（模式 B 拖拽 + 吸附） ---------------- */
window.MC_INTER_CFG[101] = {
  mode: 'sim',
  title: '拖动 $\\varphi$（自动吸附到 $\\frac{\\pi}{3}$ 的整数倍），看平移后是否与原来关于 $x$ 轴对称',
  tip: '「关于 $x$ 轴对称」就是<b>逐点取相反数</b>：要 $\\sin(x+4\\varphi)=-\\sin(x+\\varphi)$ 恒成立，即 $\\sin(x+\\varphi+3\\varphi)=-\\sin(x+\\varphi)$，于是 $3\\varphi=\\pi+2k\\pi$。在 $(0,2\\pi)$ 内 $\\varphi=\\frac{\\pi}{3},\\ \\pi,\\ \\frac{5\\pi}{3}$ 共 <b>3 个</b>。',
  view: { xr: [-0.4, 12.6], yr: [-1.7, 1.7] },
  params: [{ key: 'a', label: '相位 φ', min: 0, max: Math.PI * 2, step: 0.01, val: Math.PI, d: 2, snap: Math.PI / 3 }],
  drag: { key: 'a', xr: [0.4, 12.2], y: 1.35 },
  curves: [
    { expr: 'Math.sin(x+p.a)', color: '#2563eb', w: 2.4 },
    { expr: 'Math.sin(x+4*p.a)', color: '#dc2626', dash: true, w: 2.2 },
    { expr: '-Math.sin(x+p.a)', color: '#9aa1ab', dash: true, w: 1.4 }
  ],
  readouts: [
    { label: 'φ', expr: 'p.a', d: 3 },
    { label: '平移量 3φ', expr: '3*p.a', d: 3 },
    { label: '3φ / π', expr: '3*p.a/Math.PI', d: 3 },
    { label: '3φ 是否为 π 的奇数倍', expr: '(Math.abs(Math.sin(3*p.a))<0.03&&Math.cos(3*p.a)<0)?"是 ✓":"否 ✗"', fmt: 'raw' }
  ],
  judge: {
    expr: 'Math.abs(Math.sin(3*p.a))<0.03&&Math.cos(3*p.a)<0',
    ok: '✓ 满足条件：φ 取 $\\frac{\\pi}{3},\\pi,\\frac{5\\pi}{3}$ 之一 ⇒ 共 3 个',
    bad: '✗ 此时 3φ 不是 π 的奇数倍，平移后不关于 x 轴对称'
  },
  note: '红虚线是平移后的 $y=\\sin(x+4\\varphi)$，灰虚线是「关于 x 轴对称」的目标 $y=-\\sin(x+\\varphi)$。当红灰两条重合，条件就成立——本题答案为 C（3 个）。'
};

/* ---------------- 92 · 指数型复合函数（模式 A 分步动画） ---------------- */
window.MC_INTER_CFG[92] = {
  mode: 'steps',
  title: '跟着走一遍：分解 → 同增异减 → 单调区间 → 最大值定 $a$',
  tip: '$f(x)=\\left(\\frac13\\right)^{u}$ 是<b>外层递减</b>的复合函数，所以 $f$ 的增减与内层 $u=ax^{2}-4x+3$ <b>相反</b>——这就是「同增异减」里那个「异」。',
  bars: [
    { key: 'a', label: '参数 $a$', min: -3, max: 2, d: 2 },
    { key: 'vx', label: '内层顶点 $x$', min: -3, max: 3, d: 2 },
    { key: 'umax', label: '内层最大值 $u$', min: -2, max: 6, d: 2 },
    { key: 'fmax', label: '$f(x)$ 最大值', min: 0, max: 8, d: 3 }
  ],
  steps: [
    { tx: '① 拆成两层', vals: { a: -2, vx: 0, umax: 3, fmax: 0.037 },
      desc: '令内层 $u=ax^{2}-4x+3$，外层 $y=\\left(\\frac13\\right)^{u}$。<b>外层底数 $\\frac13<1$ ⇒ 外层关于 $u$ 单调递减</b>——记住这一点，后面全靠它。' },
    { tx: '② 同增异减', vals: { a: -2, vx: -1, umax: 5, fmax: 0.004 },
      desc: '「同增异减」：外层递减 ⇒ $f$ 与 $u$ <b>增减相反</b>。所以 $u$ 的递减区间就是 $f$ 的递增区间，$u$ 的递增区间就是 $f$ 的递减区间。' },
    { tx: '③ a=-2 求区间', vals: { a: -2, vx: -1, umax: 5, fmax: 0.004 },
      desc: '$a=-2$ 时 $u=-2x^{2}-4x+3$，开口向下、对称轴 $x=-1$：$u$ 在 $(-\\infty,-1]$ 递增、$[-1,+\\infty)$ 递减。反转过来 ⇒ $f$ 递减区间 $(-\\infty,-1]$，递增区间 $[-1,+\\infty)$。' },
    { tx: '④ 最大值定 a', vals: { a: 1, vx: 2, umax: 1, fmax: 3 },
      desc: '要 $f$ 有最大值 $3$：外层递减 ⇒ 需 $u$ 取到<b>最小值</b>。$a>0$ 时 $u$ 最小值在顶点 $x=\\frac2a$ 处为 $3-\\frac4a$，令 $\\left(\\frac13\\right)^{3-\\frac4a}=3\\Rightarrow 3-\\frac4a=-1\\Rightarrow a=1$。' }
  ],
  note: '易错：把「外层递减」记成递增，导致单调区间整体反号。检查办法：代入具体点，如 $a=-2$ 时 $f(-1)=\\left(\\frac13\\right)^{5}$ 是最小值，说明 $f$ 在 $x=-1$ 处由减转增。'
};

/* ---------------- 93 · 指数幂运算（模式 A 分步动画） ---------------- */
window.MC_INTER_CFG[93] = {
  mode: 'steps',
  title: '跟着走一遍：四个小块各自化简，最后一步相加',
  tip: '这类题不靠灵感，靠<b>逐块拆解</b>：$\\pi^{0}=1$、分数指数化根式、负指数取倒数、$\\sqrt[n]{a^{n}}=|a|$（$n$ 为偶数时<b>必须带绝对值</b>）。',
  bars: [
    { key: 't1', label: '①$3^{\\pi^0}$', min: 0, max: 5, d: 3 },
    { key: 't2', label: '②$(\\frac{25}9)^{0.5}$', min: 0, max: 3, d: 3 },
    { key: 't3', label: '③$(\\frac{64}{27})^{-\\frac23}$', min: 0, max: 3, d: 3 },
    { key: 't4', label: '④$\\sqrt[6]{(-3)^6}$', min: 0, max: 4, d: 3 }
  ],
  steps: [
    { tx: '① 3^{π⁰}', vals: { t1: 3, t2: 1, t3: 0.333, t4: 3 },
      desc: '先算指数：$\\pi^{0}=1$（<b>任何非零数的 0 次幂都是 1</b>），所以 $3^{\\pi^{0}}=3^{1}=3$。' },
    { tx: '② 分数指数', vals: { t1: 3, t2: 1.667, t3: 0.333, t4: 3 },
      desc: '$\\left(\\dfrac{25}{9}\\right)^{0.5}=\\left(\\dfrac{25}{9}\\right)^{\\frac12}=\\sqrt{\\dfrac{25}{9}}=\\dfrac{5}{3}$。$0.5=\\frac12$ 这一步别看成 $2$。' },
    { tx: '③ 负分数指数', vals: { t1: 3, t2: 1.667, t3: 0.5625, t4: 3 },
      desc: '$\\left(\\dfrac{64}{27}\\right)^{-\\frac23}$：先取倒数把负指数变正 $\\left(\\dfrac{27}{64}\\right)^{\\frac23}$，再「分母开方、分子乘方」：$\\left(\\sqrt[3]{\\dfrac{27}{64}}\\right)^{2}=\\left(\\dfrac34\\right)^{2}=\\dfrac{9}{16}$。' },
    { tx: '④ 偶次根', vals: { t1: 3, t2: 1.667, t3: 0.5625, t4: 3 },
      desc: '$\\sqrt[6]{(-3)^{6}}=|{-3}|=3$。<b>6 是偶数，结果必须是正数</b>——写成 $-3$ 是最典型的坑。' },
    { tx: '⑤ 汇总', vals: { t1: 3, t2: 1.667, t3: 0.5625, t4: 3 },
      desc: '原式 $=3+\\dfrac53\\times\\dfrac{9}{16}-3=\\dfrac{5}{3}\\times\\dfrac{9}{16}=\\dfrac{15}{16}$（前 3 与后 $-3$ 抵消）。' }
  ],
  note: '两个高频坑：①$\\sqrt[n]{a^{n}}$ 在 $n$ 为偶数时等于 $|a|$，不是 $a$；②分数指数中 $0.5=\\frac12$、$-\\frac23$ 的负号要在开方前先取倒数。'
};

/* ---------------- 94 · 指数函数真命题判断（模式 A 分步动画） ---------------- */
window.MC_INTER_CFG[94] = {
  mode: 'steps',
  title: '跟着走一遍：A 定点 → B 值域 → C 奇偶 → D 存在性，逐项判真假',
  tip: '四个选项正好对应指数函数的<b>四类考法</b>：定点（与 $a$ 无关）、值域（内层值域倒推）、奇偶（验证 $f(-x)$）、存在性（分离参数）。',
  bars: [
    { key: 'n', label: '已判定选项数', min: 0, max: 4, d: 0 }
  ],
  steps: [
    { tx: 'A · 定点', vals: { n: 1 },
      desc: 'A：$f(x)=a^{x-1}+1$。令指数为 0 即 $x=1$，$f(1)=a^{0}+1=2$，<b>与 $a$ 无关</b> ⇒ 恒过定点 $(1,2)$。<b>真命题 ✓</b>' },
    { tx: 'B · 值域', vals: { n: 2 },
      desc: 'B：$y=\\left(\\frac12\\right)^{x^{2}-1}$。内层 $u=x^{2}-1\\ge-1$，底数 $\\frac12<1$ ⇒ 递减 ⇒ $y\\le\\left(\\frac12\\right)^{-1}=2$，又 $y>0$ ⇒ 值域 $(0,2]$。<b>真命题 ✓</b>' },
    { tx: 'C · 奇偶', vals: { n: 3 },
      desc: 'C：$f(x)=\\dfrac{1}{2^{x}+1}$。算 $f(-x)=\\dfrac{1}{2^{-x}+1}=\\dfrac{2^{x}}{1+2^{x}}$，而 $-f(x)=\\dfrac{-1}{2^{x}+1}$，两者<b>不等</b> ⇒ 不是奇函数（它是「关于 $(0,\\frac12)$ 中心对称」的平移型）。<b>假命题 ✗</b>' },
    { tx: 'D · 存在性', vals: { n: 4 },
      desc: 'D：存在 $x\\in(-\\infty,0)$ 使 $x^{2}-3x+a=0$，即 $a=-x^{2}+3x$ 在 $(-\\infty,0)$ 上有解。当 $x<0$ 时 $-x^{2}+3x<0$，故需 $a<0$，与题设的某个 $a$ 范围比对即可判真假（本项为<b>假命题 ✗</b>）。' },
    { tx: '结论', vals: { n: 4 },
      desc: '综合：<b>答案 AB</b>（多选）。判定套路固定——定点看「指数为 0」，值域看「内层范围 + 底数大小」，奇偶「代 $-x$ 硬算」，存在性「分离参数转值域」。' }
  ],
  note: 'C 项是最容易误选的：$\\dfrac{1}{2^{x}+1}$ 的值域是 $(0,1)$，关于 $(0,\\frac12)$ 中心对称，它<b>不是</b>奇函数；若分子分母都改成差（$\\frac{2^x-1}{2^x+1}$）才是奇函数。'
};

/* ---------------- 97 · 奇偶函数方程组构造（模式 A 分步动画） ---------------- */
window.MC_INTER_CFG[97] = {
  mode: 'steps',
  title: '跟着走一遍：$-x$ 替换 → 联立解 $f,g$ → 单调定 $k$ → 换元求 $m$',
  tip: '「一个方程两个函数」的解法是<b>固定套路</b>：把 $x$ 换成 $-x$ 得到第二个方程，再用奇偶性改写，两式加减即得 $f$、$g$。',
  bars: [
    { key: 'k', label: '参数 $k$', min: 0, max: 3, d: 2 },
    { key: 'm', label: '参数 $m$', min: 0, max: 4, d: 3 },
    { key: 'fmax', label: '$F(x)$ 最大值', min: 0, max: 4, d: 3 }
  ],
  steps: [
    { tx: '① 换 $-x$', vals: { k: 0, m: 0, fmax: 0 },
      desc: '已知 $f(x)+g(x)=e^{x}$ …①。把 $x$ 全换成 $-x$：$f(-x)+g(-x)=e^{-x}$，用奇偶性化简为 $-f(x)+g(x)=e^{-x}$ …②。' },
    { tx: '② 联立解出', vals: { k: 1, m: 0, fmax: 0 },
      desc: '①−② 得 $2f(x)=e^{x}-e^{-x}\\Rightarrow f(x)=\\dfrac{e^{x}-e^{-x}}{2}$；①+② 得 $g(x)=\\dfrac{e^{x}+e^{-x}}{2}$。<b>验证</b>：$f$ 奇、$g$ 偶，代入原式成立 ✓' },
    { tx: '③ 单调定 k', vals: { k: 1, m: 0, fmax: 0 },
      desc: '$h(x)=kf(x)+g(x)$ 在 $\\mathbb R$ 递增 ⇔ $h\'(x)=\\frac{k}{2}(e^{x}+e^{-x})+\\frac12(e^{x}-e^{-x})\\ge0$ 恒成立。整理后用 $t=e^{x}>0$ 分析可得 $k\\ge1$。' },
    { tx: '④ 换元求 m', vals: { k: 1, m: 2.828, fmax: 2.828 },
      desc: '$F(x)=2mf(x)-g(2x)$ 在 $[0,+\\infty)$ 取最大值 $2\\sqrt2$：令 $t=e^{x}-e^{-x}\\ge0$，$g(2x)=\\frac{t^{2}+2}{2}$，化为一元二次 $F=m t-\\frac{t^{2}}{2}-1$，顶点处取最大 ⇒ $m=2\\sqrt2$。' }
  ],
  note: '第 ③ 问的关键是<b>「递增」等价于导数恒非负</b>，再用 $e^{x}+e^{-x}\\ge2$ 之类的下界把 $k$ 卡出来；第 ④ 问一定要把 $g(2x)$ 也用同一个 $t$ 表示，否则无法配成二次函数。'
};

/* ---------------- 99 · 对数函数实际应用（模式 A 分步动画） ---------------- */
window.MC_INTER_CFG[99] = {
  mode: 'steps',
  title: '跟着走一遍：认清单调性 → 区间映射 → 反解 $f$',
  tip: '对数应用题只有两步：<b>①看单调性</b>（底数 10>1 且内层递增 ⇒ $F$ 随 $f$ 递增）<b>②把 $F$ 的端点值代回去反解 $f$</b>（两边同时「取幂」）。',
  bars: [
    { key: 'F', label: '$F$ 取值（单位 $k\\lg2$）', min: 0, max: 4, d: 2 },
    { key: 'f', label: '频率 $f$ (Hz)', min: 0, max: 5200, d: 0 }
  ],
  steps: [
    { tx: '① 认单调性', vals: { F: 1, f: 0 },
      desc: '$F(f)=k\\lg\\left(1+\\dfrac{f}{700}\\right)$：底数 $10>1$ 且 $1+\\frac{f}{700}$ 随 $f$ 递增 ⇒ $F$ 关于 $f$ <b>单调递增</b>，所以 $F\\in[k\\lg2,\\ 3k\\lg2]$ 直接对应 $f$ 的一个闭区间。' },
    { tx: '② 左端反解', vals: { F: 1, f: 700 },
      desc: '令 $k\\lg\\left(1+\\dfrac{f}{700}\\right)=k\\lg2$，约掉 $k>0$ 得 $\\lg\\left(1+\\dfrac{f}{700}\\right)=\\lg2$ ⇒ $1+\\dfrac{f}{700}=2$ ⇒ $f=700$。' },
    { tx: '③ 右端反解', vals: { F: 3, f: 4900 },
      desc: '令 $k\\lg\\left(1+\\dfrac{f}{700}\\right)=3k\\lg2=k\\lg8$ ⇒ $1+\\dfrac{f}{700}=8$ ⇒ $f=7\\times700=4900$。' },
    { tx: '④ 写区间', vals: { F: 3, f: 4900 },
      desc: '由单调性，$F\\in[k\\lg2,3k\\lg2]$ ⇔ $f\\in[700,\\ 4900]$（单位 Hz）。<b>端点闭合</b>：区间型条件取等。' }
  ],
  note: '易错：①忘记 $k>0$ 才能约掉并保持不等号方向；②$3k\\lg2=k\\lg2^{3}=k\\lg8$ 这一步合并系数，避免把 $3k\\lg2$ 直接写成 $\\lg(2\\cdot3)$。'
};

/* ---------------- 100 · 函数性质对称周期零点（模式 B 拖拽） ---------------- */
window.MC_INTER_CFG[100] = {
  mode: 'sim',
  title: '拖动 $a$，看「偶函数 + 反周期」如何把 $[0,1]$ 上的一小段拼成整条图象',
  tip: '两条性质叠加：<b>①偶函数</b> $f(-x)=f(x)$ 决定左半边；<b>②$f(1-x)=-f(1+x)$</b> 即 $f(x+2)=-f(x)$（<b>反周期</b>）⇒ 每 2 个单位取相反数 ⇒ 周期 $T=4$。',
  view: { xr: [-1.6, 4.6], yr: [-2.8, 2.8] },
  params: [{ key: 'a', label: '参数 a（$f(x)=x^2+2x-a$）', min: 0, max: 5, step: 0.5, val: 3, d: 1 }],
  drag: { key: 'a', xr: [-1.4, 4.4], y: 2.45 },
  /* 每段一条曲线、用 domain 隔开：反周期在整数点会跳变，交给引擎断笔 */
  curves: [
    { expr: '(x*x-2*x-p.a)', color: '#2563eb', w: 2.4, domain: 'x>=-1.55&&x<0' },
    { expr: '(x*x+2*x-p.a)', color: '#2563eb', w: 2.4, domain: 'x>=0&&x<1' },
    { expr: '(-((2-x)*(2-x)+2*(2-x)-p.a))', color: '#2563eb', w: 2.4, domain: 'x>=1&&x<2' },
    { expr: '(-((x-2)*(x-2)+2*(x-2)-p.a))', color: '#2563eb', w: 2.4, domain: 'x>=2&&x<3' },
    { expr: '((4-x)*(4-x)+2*(4-x)-p.a)', color: '#2563eb', w: 2.4, domain: 'x>=3&&x<4.55' },
    { expr: '(-((2-x)*(2-x)+2*(2-x)-p.a))', color: '#1a8f5f', w: 3.6, domain: 'x>=1&&x<2' }
  ],
  custom: function (ctx, p, U) {
    /* 对称轴 x=0（偶函数）与中心对称点 (1,0)，以及 C 项那段的文字标注 */
    ctx.strokeStyle = '#b8720e'; ctx.lineWidth = 1.2; ctx.setLineDash([5, 4]);
    ctx.beginPath(); ctx.moveTo(U.xx(0), U.t); ctx.lineTo(U.xx(0), U.CH - U.pad.b); ctx.stroke();
    ctx.setLineDash([]);
    ctx.beginPath(); ctx.arc(U.xx(1), U.yy(0), 5, 0, Math.PI * 2);
    ctx.fillStyle = '#dc2626'; ctx.fill();
    ctx.fillStyle = '#dc2626'; ctx.font = '600 11px system-ui'; ctx.textAlign = 'left';
    ctx.fillText('(1,0) 中心对称', U.xx(1) + 8, U.yy(0) - 8);
    ctx.fillStyle = '#1a8f5f'; ctx.textAlign = 'center';
    ctx.fillText('C 项：x∈[5,6] 平移回来就是这段', U.xx(1.5), U.yy(-2.45));
  },
  readouts: [
    { label: 'f(1)（需为 0）', expr: '1+2-p.a', d: 1 },
    { label: 'f(-1) = f(1)', expr: '1+2-p.a', d: 1 },
    { label: 'f(2019)（2019≡3 mod 4）', expr: '-(1+2-p.a)', d: 1 },
    { label: 'f(2025)（2025≡1 mod 4）', expr: '1+2-p.a', d: 1 }
  ],
  judge: {
    expr: 'p.a===3',
    ok: '✓ a=3 ⇒ f(1)=0，于是 f(-1)=f(2019)=f(2025)=0 ⇒ B 项和为零成立',
    bad: '✗ 只有 a=3 才能让 f(1)=0（对称式令 x=0 即得 3-a=0）'
  },
  note: '绿线是 C 项说的 $x\in[5,6]$（由 $T=4$ 平移到 $[1,2]$）——它正是 $-x^{2}+14x-45$。本题答案 <b>BCD</b>（A 错：$a=3$ 不是 2）。'
};
