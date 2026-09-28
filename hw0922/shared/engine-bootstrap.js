/* =========================================================================
 * 「记忆卡命中分析与生成」模块自动挂载段（由 install.py 追加到 shared/engine.js）
 * -------------------------------------------------------------------------
 * 本段自身不含业务逻辑，只负责在 2026-09-22 数学作业讲解页加载模块：
 *     shared/mc-fit-gen.js   （逻辑）
 *     shared/mc-fit-gen.css  （样式，模块自己注入）
 *     shared/mc-fit-0922.json（本题命中卡 + 待生成卡数据）
 * 其它页面（物理 317/318 等）匹配不到文件名，零开销直接返回。
 * 想扩到别的作业：把正则里的 0922_m\d+ 改成对应的文件名前缀即可。
 * ========================================================================= */
(function () {
  'use strict';
  try {
    if (window.__mcFitBooted) return;
    var file = (location.pathname || '').split('/').pop() || '';
    try { file = decodeURIComponent(file); } catch (e) {}
    if (!/^0922_m\d+/.test(file)) return;
    window.__mcFitBooted = true;
    if (document.getElementById('mc-fit-gen-js')) return;
    var cur = document.currentScript;
    var base = (cur && cur.src) ? cur.src.replace(/[^\/]*$/, '') : 'shared/';
    window.MC_FIT_BASE = base;
    var s = document.createElement('script');
    s.id = 'mc-fit-gen-js';
    s.src = base + 'mc-fit-gen.js';
    s.async = false;
    (document.head || document.documentElement).appendChild(s);
  } catch (e) { /* 静默：注入失败不影响页面原有功能 */ }
})();
