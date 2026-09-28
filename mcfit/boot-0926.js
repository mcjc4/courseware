/* =========================================================================
 * boot-0926.js —— 0926 数学错题批（lesson 87~101）命中分析模块启动器
 * -------------------------------------------------------------------------
 * 各单题课件页 </body> 前引一行：
 *     <script src="../../mcfit/boot-0926.js"></script>
 * 只在 lessons/87~101 目录下激活，其它页面零开销直接返回。
 * 激活后设置 window.MC_FIT_CFG 并加载 ../mcfit/mc-fit-gen.js（参数化引擎）。
 * ========================================================================= */
(function () {
  'use strict';
  try {
    if (window.__mcFitBooted) return;
    var path = location.pathname || '';
    try { path = decodeURIComponent(path); } catch (e) {}
    if (!/\/lessons\/(?:8[7-9]|9\d|10[01])-[^\/]+\/(?:index\.html)?$/.test(path)) return;
    window.__mcFitBooted = true;
    window.MC_FIT_CFG = {
      json: 'mc-fit-0926.json',
      sourceId: 'hw-2026-09-26-math',
      /* ⚠️ 「待训练」必须显式带上：记忆卡应用的「📚 训练库」只聚合
       *    cards 表中 tags 含「待训练」的行，缺这个标签 = 生成了也练不到。
       *    且课件页必须与记忆卡应用同源（jikaka-memory），否则 WB Cloud 跨域被 CORS 拦死。 */
      tags: ['hw-0926', '错题', '待训练'],
      anchor: 'qcard'
    };
    if (document.getElementById('mc-fit-gen-js')) return;
    var cur = document.currentScript;
    var base = (cur && cur.src) ? cur.src.replace(/[^\/]*$/, '') : '../../mcfit/';
    window.MC_FIT_BASE = base;
    var s = document.createElement('script');
    s.id = 'mc-fit-gen-js';
    s.src = base + 'mc-fit-gen.js';
    s.async = false;
    (document.head || document.documentElement).appendChild(s);
  } catch (e) { /* 静默：注入失败不影响页面原有功能 */ }
})();
