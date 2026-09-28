/* =========================================================================
 * mc-fit-gen.js —— 「记忆卡命中分析与生成」模块（自挂载，零依赖）
 * -------------------------------------------------------------------------
 * 用法：在讲解页 </body> 前加一行
 *     <script src="shared/mc-fit-gen.js"></script>
 * 模块自行：
 *   1) 注入 shared/mc-fit-gen.css（无需改 <head>）
 *   2) 读取 shared/mc-fit-0922.json，按当前页文件名定位本题数据
 *   3) 把自己挂到「答案分析」章节（选项判定）之后
 *   4) 渲染：命中卡（记忆库已有，按契合度排序）+ 待生成新卡（按 SOP 原子拆解）
 *   5) 「通过入库」→ 写 WB Cloud cards 表；失败则落本地队列并可导出 JSON
 *
 * 数据契约（mc-fit-0922.json）：
 *   meta  : {title, homework, library, libraryStats{cards,nextRow,nextId}, total}
 *   pages : [{q, page, title, chapter, src, verdict,
 *             hits:[{fit, level, chapter, signal, conclusion, file, link}],
 *             newCards:[{id, chapter, signal, conclusion, orig, src, remark, link}]}]
 * ========================================================================= */
(function () {
  'use strict';

  // 资源基址：优先用注入方（engine.js）传入的 MC_FIT_BASE，其次用自身 <script src>
  var BASE = (function () {
    try {
      if (window.MC_FIT_BASE) return window.MC_FIT_BASE;
      var c = document.currentScript;
      if (c && c.src) return c.src.replace(/[^\/]*$/, '');
    } catch (e) {}
    return 'shared/';
  })();

  /* 页面级覆写：注入方在加载本文件前设 window.MC_FIT_CFG =
     { json:'mc-fit-0926.json', sourceId:'hw-2026-09-26-math', tags:['hw-0926','错题'], anchor:'qcard', qMatch:'…' }
     不设置则沿用 0922 默认值（老页面零影响）。 */
  var XC = window.MC_FIT_CFG || {};

  var CFG = {
    jsonUrl: BASE + (XC.json || 'mc-fit-0922.json'),
    cssUrl: BASE + 'mc-fit-gen.css',
    table: 'cards',
    viewTable: 'page_views',          // 浏览埋点表：page/hw/title/viewer/viewed_at
    sourceId: XC.sourceId || 'hw-2026-09-22-math',
    endpoint: 'https://jikaka-memory.app.workbuddy.host',
    publishableKey: 'wbpk_QuSSvKgXD7uP73LA5D5gNT_W0t84UkhE7UB0e9poO19fS9ZgJR6WlOP',
    sdkSrc: [
      'https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js',
      'https://unpkg.com/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js'
    ]
  };

  var K = {
    edit: 'mcfit_edit_v1',
    approve: 'mcfit_approve_v1',
    queue: 'mcfit_queue_v1',
    train: 'mcfit_train_v1',
    hitEdit: 'mcfit_hitedit_v1'
  };

  var S = { data: null, page: null, el: null, db: null, cloudState: 'idle' };

  /* ------------------------------------------------ 小工具 */
  function $(sel, root) { return (root || document).querySelector(sel); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function lsGet(k, d) {
    try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; }
  }
  function lsSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } }
  function nowIso() { return new Date().toISOString(); }
  function pageKey() {
    var p = (location.pathname || '').split('/').pop() || '';
    try { p = decodeURIComponent(p); } catch (e) {}
    return p;
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
    if ($('#mcFitGenCss')) return;
    var l = document.createElement('link');
    l.id = 'mcFitGenCss'; l.rel = 'stylesheet'; l.href = CFG.cssUrl;
    (document.head || document.documentElement).appendChild(l);
  }

  /* ------------------------------------------------ 云端 */
  function loadSdk() {
    return new Promise(function (res) {
      if (window.__mcfitSdkFail) return res(false);
      if (typeof window.WorkBuddyCloud !== 'undefined') return res(true);
      var i = 0;
      (function next() {
        if (typeof window.WorkBuddyCloud !== 'undefined') return res(true);
        if (i >= CFG.sdkSrc.length) { window.__mcfitSdkFail = true; return res(false); }
        var s = document.createElement('script');
        s.src = CFG.sdkSrc[i++];
        s.onload = function () { typeof window.WorkBuddyCloud !== 'undefined' ? res(true) : next(); };
        s.onerror = next;
        (document.head || document.documentElement).appendChild(s);
      })();
    });
  }
  function getDb() {
    if (S.db) return Promise.resolve(S.db);
    return loadSdk().then(function (ok) {
      if (!ok) return null;
      try {
        var c = window.WorkBuddyCloud.createWorkBuddyCloud({
          endpoint: CFG.endpoint, publishableKey: CFG.publishableKey
        });
        S.db = c.database;
        return S.db;
      } catch (e) { return null; }
    });
  }
  /* WB Cloud cards 表实际列：card_id / subject / signal / conclusion / chapter /
     src / tags(jsonb) / link / note / orig / updated_at。
     id 约定沿用站点既有风格「前缀:科目:编号」，本模块用 hw 前缀区分作业生成来源。 */
  function toRow(c) {
    return {
      card_id: 'hw:数学:' + c.id,
      subject: '数学',
      chapter: c.chapter,
      signal: c.signal,
      conclusion: c.conclusion,
      orig: c.orig || '',
      src: c.src,
      link: c.link || '',
      note: c.remark ? (c.remark + '｜source_id=' + CFG.sourceId) : ('source_id=' + CFG.sourceId),
      tags: XC.tags || ['hw-0922', '二次函数与幂函数', '幂函数'],
      updated_at: nowIso()
    };
  }
  function cloudUpsert(rows) {
    return getDb().then(function (db) {
      if (!db) return false;
      return Promise.resolve(db.from(CFG.table).upsert(rows, { onConflict: 'card_id' }))
        .then(function (r) { return !(r && r.error); })
        .catch(function () { return false; });
    });
  }

  /* 浏览埋点：每次打开讲解页往 page_views 记一行（page/hw/title/viewer/viewed_at）。
     viewer 取 ?viewer= 参数或 localStorage('mcfit_viewer')，缺省空。失败静默，绝不影响页面。 */
  function trackView(p) {
    getDb().then(function (db) {
      if (!db) return;
      var viewer = '';
      try {
        var m = location.search.match(/[?&]viewer=([^&]+)/);
        viewer = m ? decodeURIComponent(m[1]) : (localStorage.getItem('mcfit_viewer') || '');
      } catch (e) {}
      Promise.resolve(db.from(CFG.viewTable).insert([{
        page: p.page, hw: CFG.sourceId, title: p.title || '',
        viewer: viewer, viewed_at: nowIso()
      }])).catch(function () {});
    });
  }

  /* ------------------------------------------------ 数据准备 */
  function applyEdits(page) {
    var ed = lsGet(K.edit, {});
    var he = lsGet(K.hitEdit, {});
    page.newCards = (page.newCards || []).map(function (c) {
      return ed[c.id] ? Object.assign({}, c, ed[c.id]) : c;
    });
    page.hits = (page.hits || []).map(function (h, i) {
      var hid = 'h' + i + ':' + (h.chapter || '');
      return he[hid] ? Object.assign({}, h, he[hid]) : Object.assign({}, h, { __hid: hid });
    });
    return page;
  }

  /* ------------------------------------------------ 渲染 */
  function scoreCls(f) { return f >= 75 ? 'hi' : (f >= 50 ? 'mid' : 'lo'); }

  function hitBody(h, q) {
    return '' +
      '<div class="mg-rel"><b>🔗 与本题的关系：</b>本题考「' + esc(q.chapter) +
      '」，该卡覆盖「' + esc(h.chapter) + '」（契合度 <b>' + h.fit + '</b>，' + esc(h.level) + '）</div>' +
      fld('信号', h.signal) + fld('结论', h.conclusion) +
      (h.file ? '<div class="mg-f"><span class="lbl">出处</span>' + esc(h.file) + '</div>' : '') +
      '<div class="mg-bar">' +
      '<button class="mg-btn" data-act="hit-edit" data-h="' + esc(h.__hid) + '">✏️ 编辑</button>' +
      '<button class="mg-btn gray" data-act="train" data-id="' + esc((h.chapter || '') + '|' + h.fit) + '">🏋️ 加入训练</button>' +
      '<span class="mg-saved" data-saved="' + esc(h.__hid) + '" style="display:none"></span>' +
      '</div>';
  }

  function newBody(c, q) {
    var ap = lsGet(K.approve, {});
    var done = !!ap[c.id];
    return '' +
      '<div class="mg-rel"><b>🎯 生成依据：</b>本题（' + esc(q.chapter) + '）的该原子知识点在记忆库中未命中，' +
      '按「错题整理」SOP 拆为独立信号卡——一张卡只承载一个知识点。</div>' +
      fld('原题题干', c.orig) + fld('题干信号', c.signal) + fld('结论/易错点', c.conclusion) +
      '<div class="mg-f"><span class="lbl">出处</span>' + esc(c.src) +
      (c.remark ? '　<span class="lbl">备注</span>' + esc(c.remark) : '') + '</div>' +
      '<div class="mg-bar">' +
      '<button class="mg-btn" data-act="new-edit" data-id="' + esc(c.id) + '">✏️ 编辑</button>' +
      '<button class="mg-btn ' + (done ? 'gray' : 'pri') + '" data-act="approve" data-id="' + esc(c.id) + '"' +
      (done ? ' disabled' : '') + '>' + (done ? '✅ 已入库' : '⏫ 通过并入库') + '</button>' +
      '<button class="mg-btn gray" data-act="copy" data-id="' + esc(c.id) + '">📋 复制</button>' +
      '<span class="mg-saved" data-saved="' + esc(c.id) + '" style="display:none"></span>' +
      '</div>';
  }

  function fld(label, val) {
    if (val == null || val === '') val = '（空）';
    return '<div class="mg-f" data-f="' + esc(label) + '"><span class="lbl">' + esc(label) + '</span>' + esc(val) + '</div>';
  }

  function cardHtml(kind, id, chapter, badge, body, extraCls) {
    return '<div class="mg-card ' + (extraCls || '') + '" data-kind="' + kind + '" data-id="' + esc(id) + '">' +
      '<div class="mg-head" data-act="toggle">' +
      (kind === 'new' ? '<span class="mg-id">' + esc(id) + '</span>' : '') +
      '<span class="mg-ch">' + esc(chapter) + '</span>' +
      badge +
      '<span class="mg-chev">▸</span>' +
      '</div>' +
      '<div class="mg-body">' + body + '</div>' +
      '</div>';
  }

  function hitBadge(h) {
    return '<span class="mg-score ' + scoreCls(h.fit) + '"><b>' + h.fit + '</b><span>契合度</span></span>';
  }

  function render() {
    var p = S.page, m = S.data.meta;
    if (!p) return;
    var ap = lsGet(K.approve, {});
    var approvedN = (p.newCards || []).filter(function (c) { return ap[c.id]; }).length;
    var best = (p.hits || []).slice().sort(function (a, b) { return b.fit - a.fit; })[0];
    var lib = (m.libraryStats || {});

    var hitsHtml = (p.hits && p.hits.length)
      ? '<div class="mg-list">' + p.hits.map(function (h) {
        return cardHtml('hit', (h.chapter || '') + '|' + h.fit, h.chapter, hitBadge(h), hitBody(h, p), '');
      }).join('') + '</div>'
      : '<div class="mg-empty">本题在记忆库中未找到相关旧卡——全部知识点都需要新建。</div>';

    var newHtml = (p.newCards && p.newCards.length)
      ? '<div class="mg-list">' + p.newCards.map(function (c) {
        var st = ap[c.id];
        var done = !!st;
        var txt = !done ? '待入库'
          : (st.cloud === true ? '已入库' : (st.cloud === false ? '待补录(本机)' : '已提交…'));
        var badge = '<span class="mg-flag' + (done && st.cloud !== false ? ' done' : '') + '">' + txt + '</span>';
        return cardHtml('new', c.id, c.chapter, badge, newBody(c, p), done ? 'approved' : 'new');
      }).join('') + '</div>'
      : '<div class="mg-empty">本题知识点已被记忆库覆盖，无需新增卡。</div>';

    var html = '' +
      '<h2><span class="dot"></span>🎯 记忆卡命中分析与生成</h2>' +
      '<div class="mg-sum">' +
      '<div class="mg-stat"><b>' + (p.hits || []).length + '</b><span>命中记忆卡</span></div>' +
      '<div class="mg-stat"><b class="mg-hi">' + ((p.newCards || []).length - approvedN) + '</b><span>待生成新卡</span></div>' +
      '<div class="mg-stat"><b>' + (best ? best.fit : '–') + '</b><span>' + (best ? '最高契合度' : '最高命中') + '</span></div>' +
      '<span class="mg-src">库：' + esc(m.library || '') + '（原有 ' + (lib.cards == null ? '?' : lib.cards) + ' 张' +
      (lib.added ? ' → 本批 +' + lib.added + ' → ' + (lib.cardsAfter || '?') + ' 张' : '') +
      ' · 自第 ' + (lib.nextRow || '?') + ' 行续' +
      (lib.nextId ? ' · 编号 ' + esc(lib.nextId) + (lib.lastId ? '~' + esc(lib.lastId) : '') : '') + '）</span>' +
      '</div>' +
      '<div class="mg-hint"><b>判定：</b>' + esc(p.verdict) + '　<b>答案</b>见上方分析；命中卡直接练，' +
      '未命中的知识点按原子信号生成新卡，通过入库后写入云端 <code>cards</code> 表与记忆库 Excel（从末行续）。</div>' +
      '<div class="mg-sec"><span class="mg-t">📚 命中：记忆库已有卡</span>' +
      '<span class="mg-n">' + (p.hits || []).length + '</span>' +
      '<span class="mg-sub">按契合度排序，点击展开看信号与结论</span></div>' + hitsHtml +
      '<div class="mg-sec"><span class="mg-t">✨ 生成：本题新增原子卡</span>' +
      '<span class="mg-n blue">' + (p.newCards || []).length + '</span>' +
      '<span class="mg-sub">一条信号一张卡，可编辑后逐张入库</span></div>' + newHtml +
      '<div class="mg-foot">' +
      '<button class="mg-btn pri" data-act="approve-all">⏫ 全部通过并入库</button>' +
      '<button class="mg-btn" data-act="expand">展开全部</button>' +
      '<button class="mg-btn" data-act="collapse">收起全部</button>' +
      '<button class="mg-btn gray" data-act="export">⬇ 导出 JSON</button>' +
      '<span class="mg-status" data-status>就绪</span>' +
      '</div>';

    S.el.innerHTML = html;
    renderMath(S.el);
  }

  /* ------------------------------------------------ 交互 */
  function setStatus(txt, cls) {
    var el = $('[data-status]', S.el);
    if (el) { el.textContent = txt; el.className = 'mg-status' + (cls ? ' ' + cls : ''); }
  }
  function flash(cardId, txt, warn) {
    var el = $('[data-saved="' + cardId + '"]', S.el);
    if (!el) return;
    el.style.display = 'inline';
    el.className = 'mg-saved' + (warn ? ' warn' : '');
    el.textContent = txt;
    setTimeout(function () { el.style.display = 'none'; }, 5000);
  }
  function findNew(id) {
    return (S.page.newCards || []).filter(function (c) { return c.id === id; })[0];
  }

  function approve(card) {
    var q = lsGet(K.queue, {});
    var ap = lsGet(K.approve, {});
    q[card.id] = Object.assign({}, toRow(card), { queued_at: nowIso() });
    lsSet(K.queue, q);
    ap[card.id] = { at: nowIso(), cloud: null };
    lsSet(K.approve, ap);
    setStatus('☁ ' + card.id + ' 入库中…');
    return cloudUpsert([toRow(card)]).then(function (ok) {
      ap[card.id] = { at: nowIso(), cloud: !!ok };
      lsSet(K.approve, ap);
      render();                       // 先重建（会重置状态条），再写提示
      if (ok) {
        setStatus('✅ ' + card.id + ' 已入库（云端 cards 表）', 'ok');
        flash(card.id, '✅ 已同步云端');
      } else {
        setStatus('⚠️ ' + card.id + '：云端不可达，已存入本地待入库队列（点「导出 JSON」可补录）', 'warn');
        flash(card.id, '⚠️ 仅本机队列', true);
      }
      return ok;
    });
  }

  function approveAll() {
    var ap = lsGet(K.approve, {});
    var todo = (S.page.newCards || []).filter(function (c) { return !ap[c.id]; });
    if (!todo.length) { setStatus('全部已入库', 'ok'); return; }
    setStatus('☁ 批量入库 ' + todo.length + ' 张…');
    var rows = todo.map(toRow);
    var q = lsGet(K.queue, {});
    todo.forEach(function (c) { q[c.id] = Object.assign({}, toRow(c), { queued_at: nowIso() }); ap[c.id] = { at: nowIso(), cloud: null }; });
    lsSet(K.queue, q); lsSet(K.approve, ap);
    cloudUpsert(rows).then(function (ok) {
      todo.forEach(function (c) { ap[c.id] = { at: nowIso(), cloud: !!ok }; });
      lsSet(K.approve, ap);
      render();
      if (ok) { setStatus('✅ ' + rows.length + ' 张已全部入库（云端 cards 表）', 'ok'); }
      else { setStatus('⚠️ 云端不可达，' + rows.length + ' 张已存入本地待入库队列（点「导出 JSON」可补录）', 'warn'); }
    });
  }

  function exportJson() {
    var ap = lsGet(K.approve, {});
    var all = (S.page.newCards || []).map(toRow);
    var picked = all.filter(function (r) { return ap[r.card_id]; });
    var payload = {
      homework: S.data.meta.homework, page: S.page.page, q: S.page.q,
      exported_at: nowIso(), cloud_ok: false,
      cards: picked.length ? picked : all
    };
    try {
      var blob = new Blob([JSON.stringify(payload, null, 1)], { type: 'application/json' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'mcfit-' + S.page.page.replace(/\.html$/, '') + '.json';
      document.body.appendChild(a); a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
      setStatus('已导出 ' + payload.cards.length + ' 张卡的 JSON', 'ok');
    } catch (e) { setStatus('导出失败：' + e.message, 'warn'); }
  }

  function editCard(kind, id) {
    var card = kind === 'new' ? findNew(id) : null;
    var hid = kind === 'hit' ? id : null;
    var hit = null;
    if (kind === 'hit') {
      hit = (S.page.hits || []).filter(function (h) { return h.__hid === hid; })[0];
      if (!hit) {
        var parts = String(id).split('|'); var ch = parts.slice(0, parts.length - 1).join('|');
        hit = (S.page.hits || []).filter(function (h) { return h.chapter === ch; })[0];
      }
    }
    var obj = card || hit;
    if (!obj) return;
    var body = $('.mg-card[data-id="' + String(id).replace(/"/g, '\\"') + '"] .mg-body', S.el);
    if (!body) return;
    var keys = card ? [['orig', '原题题干'], ['signal', '题干信号'], ['conclusion', '结论/易错点']]
      : [['signal', '信号'], ['conclusion', '结论']];
    var h = '<div class="mg-rel">✏️ 编辑中——保存后写本机缓存（命中卡不再回写记忆库原表，生成卡会随入库一并提交）。</div>';
    keys.forEach(function (kv) {
      h += '<div class="mg-f"><span class="lbl">' + kv[1] + '</span><textarea data-k="' + kv[0] + '" rows="3">' +
        esc(obj[kv[0]]) + '</textarea></div>';
    });
    h += '<div class="mg-bar">' +
      '<button class="mg-btn pri" data-act="save" data-kind="' + kind + '" data-id="' + esc(id) + '">💾 保存</button>' +
      '<button class="mg-btn gray" data-act="cancel" data-kind="' + kind + '" data-id="' + esc(id) + '">取消</button>' +
      '</div>';
    body.innerHTML = h;
    renderMath(body);
  }

  function saveEdit(kind, id) {
    var card = $('.mg-card[data-id="' + String(id).replace(/"/g, '\\"') + '"]', S.el);
    if (!card) return;
    var body = $('.mg-body', card);
    var vals = {};
    body.querySelectorAll('textarea[data-k]').forEach(function (t) { vals[t.getAttribute('data-k')] = t.value; });
    if (kind === 'new') {
      var ed = lsGet(K.edit, {});
      ed[id] = Object.assign({}, ed[id] || {}, vals, { edited_at: nowIso() });
      lsSet(K.edit, ed);
      var c = findNew(id);
      if (c) Object.assign(c, vals);
    } else {
      var he = lsGet(K.hitEdit, {});
      var key = String(id).indexOf('|') >= 0 ? id.replace(/\|\d+$/, '') : id;
      he[key] = Object.assign({}, he[key] || {}, vals, { edited_at: nowIso() });
      lsSet(K.hitEdit, he);
      var parts = String(id).split('|'); var ch = parts.slice(0, parts.length - 1).join('|');
      (S.page.hits || []).forEach(function (h) { if (h.chapter === ch) Object.assign(h, vals); });
    }
    render();
    var t = $('.mg-card[data-id="' + String(id).replace(/"/g, '\\"') + '"]', S.el);
    if (t) t.classList.add('open');
    flash(id, '✅ 已保存（本机）');
  }

  function copyCard(id) {
    var c = findNew(id);
    if (!c) return;
    var txt = [c.id, c.chapter, '题干：' + c.orig, '信号：' + c.signal, '结论：' + c.conclusion,
      '出处：' + c.src, c.remark ? '备注：' + c.remark : ''].filter(Boolean).join('\n');
    try {
      navigator.clipboard.writeText(txt);
      flash(id, '📋 已复制');
    } catch (e) {
      var ta = document.createElement('textarea');
      ta.value = txt; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); flash(id, '📋 已复制'); } catch (e2) { flash(id, '复制失败', true); }
      ta.remove();
    }
  }

  function toggleTrain(btn) {
    var id = btn.getAttribute('data-id');
    var m = lsGet(K.train, {});
    if (m[id]) { delete m[id]; btn.textContent = '🏋️ 加入训练'; btn.className = 'mg-btn gray'; }
    else { m[id] = { train_tag: '待训练', at: nowIso() }; btn.textContent = '✓ 已加入训练'; btn.className = 'mg-btn ok'; }
    lsSet(K.train, m);
  }

  function onClick(e) {
    var t = e.target.closest('[data-act]');
    if (!t || !S.el.contains(t)) return;
    var act = t.getAttribute('data-act');
    if (act === 'toggle') {
      var card = t.closest('.mg-card');
      if (card && !e.target.closest('button')) card.classList.toggle('open');
      return;
    }
    if (act === 'new-edit') { e.stopPropagation(); return editCard('new', t.getAttribute('data-id')); }
    if (act === 'hit-edit') { e.stopPropagation(); return editCard('hit', t.getAttribute('data-h')); }
    if (act === 'save') { e.stopPropagation(); return saveEdit(t.getAttribute('data-kind'), t.getAttribute('data-id')); }
    if (act === 'cancel') { e.stopPropagation(); return render(); }
    if (act === 'approve') {
      e.stopPropagation();
      var c = findNew(t.getAttribute('data-id'));
      if (c) approve(c);
      return;
    }
    if (act === 'approve-all') { e.stopPropagation(); return approveAll(); }
    if (act === 'copy') { e.stopPropagation(); return copyCard(t.getAttribute('data-id')); }
    if (act === 'train') { e.stopPropagation(); return toggleTrain(t); }
    if (act === 'export') { e.stopPropagation(); return exportJson(); }
    if (act === 'expand') {
      S.el.querySelectorAll('.mg-card').forEach(function (c) { c.classList.add('open'); });
      return;
    }
    if (act === 'collapse') {
      S.el.querySelectorAll('.mg-card').forEach(function (c) { c.classList.remove('open'); });
      return;
    }
  }

  /* ------------------------------------------------ 挂载 */
  function findAnchor() {
    /* 课件站单题页（XC.anchor==='qcard'）：挂在最后一个 section.qcard 之后 */
    if (XC.anchor === 'qcard') {
      var qc = document.querySelectorAll('section.qcard');
      if (qc.length) {
        var last = qc[qc.length - 1];
        return { after: last };
      }
      return { before: null };
    }
    var secs = [].slice.call(document.querySelectorAll('section.card'));
    var i, h;
    for (i = 0; i < secs.length; i++) {
      h = $('h2', secs[i]);
      if (h && /选项判定|答案分析|答案核对/.test(h.textContent || '')) return { after: secs[i] };
    }
    for (i = 0; i < secs.length; i++) {
      h = $('h2', secs[i]);
      if (h && /分步讲解|分步解析|分步/.test(h.textContent || '')) return { before: secs[i] };
    }
    return { before: null };
  }

  /* 页面原有的「🎯 记忆卡命中分析」区块：本模块是它的超集，就地隐藏避免重复 */
  function hideLegacy() {
    var old = document.getElementById('fitCard');
    if (old && old !== S.el) {
      old.style.display = 'none';
      old.setAttribute('data-mcfit-legacy', '1');
    }
  }

  function mount() {
    if (document.getElementById('mcFitCard')) return;
    var sec = document.createElement('section');
    sec.className = 'card';
    sec.id = 'mcFitCard';
    var a = findAnchor();
    if (a.after) { a.after.parentNode.insertBefore(sec, a.after.nextSibling); }
    else if (a.before) { a.before.parentNode.insertBefore(sec, a.before); }
    else {
      var host = document.querySelector('main') || document.querySelector('.wrap') ||
        document.querySelector('.container') || document.body;
      host.appendChild(sec);
    }
    S.el = sec;
    sec.addEventListener('click', onClick);
    hideLegacy();
  }

  /* ------------------------------------------------ 启动 */
  function pickPage(data) {
    /* 1) page 字段与当前路径后缀匹配（支持 lessons/xxx/index.html 与 /lessons/xxx/ 两种）
       2) 退回文件名精确匹配（0922 风格）
       3) 退回题号正则（XC.qMatch 可覆写，默认 0922_m(\d+)） */
    var path = (location.pathname || '').replace(/^\//, '');
    try { path = decodeURIComponent(path); } catch (e) {}
    var i, pg;
    for (i = 0; i < data.pages.length; i++) {
      pg = data.pages[i].page || '';
      if (!pg) continue;
      if (path === pg || (pg.length && path.slice(-pg.length) === pg) ||
          path.indexOf('/' + pg) !== -1 || path.indexOf(pg.replace(/\/index\.html$/, '/') + '') !== -1) return data.pages[i];
    }
    var f = pageKey();
    for (i = 0; i < data.pages.length; i++) if (data.pages[i].page === f) return data.pages[i];
    var mr = null;
    try { mr = XC.qMatch ? new RegExp(XC.qMatch) : null; } catch (e) { mr = null; }
    var m = (f.match(mr || /0922_m(\d+)/)) || (path.match(mr || /0922_m(\d+)/));
    if (m) {
      var q = parseInt(m[1], 10);
      for (i = 0; i < data.pages.length; i++) if (data.pages[i].q === q) return data.pages[i];
    }
    return null;
  }

  function boot() {
    injectCss();
    fetch(CFG.jsonUrl, { cache: 'no-cache' })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || !data.pages) throw new Error('数据格式异常');
        var p = pickPage(data);
        if (!p) {
          var t = document.querySelector('main') || document.body;
          var d = document.createElement('div');
          d.className = 'mg-empty';
          d.textContent = '本页未在 ' + CFG.jsonUrl.replace(/^.*\//, '') + ' 中找到对应题目数据（' + pageKey() + '）。';
          t.appendChild(d);
          return;
        }
        S.data = data;
        S.page = applyEdits(p);
        mount();
        render();
        setStatus('已载入 ' + S.page.page);
        trackView(S.page);
      })
      .catch(function (e) {
        var t = document.querySelector('main') || document.body;
        var d = document.createElement('div');
        d.className = 'mg-empty';
        d.textContent = '记忆卡模块数据加载失败（' + CFG.jsonUrl + '）：' + e.message;
        t.appendChild(d);
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  window.MCFitGen = { boot: boot, state: S, cfg: CFG };
})();
