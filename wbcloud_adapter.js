/* =========================================================================
 * WorkBuddy Cloud 适配器（解题库 / 课件页共用）
 * -------------------------------------------------------------------------
 * 目标：把课件页对 Supabase REST 的裸 fetch 透明翻译成 WB Cloud SDK 调用，
 *       页面原生云端代码（DEFAULT_CLOUD / CFG / fetchCloudRow / pushCloud /
 *       cloudNotes / delCloud / subscribeRealtime）一律不改，只注入本文件。
 *
 * 课件库与记忆卡合并到同一 WB Cloud 应用（同源 jikaka-memory，免跨域预检）：
 *   wbapp_QuSSvKgXD7uP73LA5D5gNT —— 课件页挂载在 jikaka-memory.app.workbuddy.host/courseware/，
 *   与记忆卡 cards/knowledge 后端同源，课件页可直接写 course_stats/course_notes 与 cards。
 *   endpoint      = https://jikaka-memory.app.workbuddy.host
 *   publishableKey= wbpk_QuSSvKgXD7uP73LA5D5gNT_W0t84UkhE7UB0e9poO19fS9ZgJR6WlOP
 *
 * 原理：
 *   1) 动态加载 WB Cloud SDK（jsdelivr 主 / unpkg 备），就绪后建 client.database。
 *   2) 覆盖 window.fetch：凡命中 *.supabase.co/rest/v1/ 的请求 → 走 wbFetchRest，
 *      翻译成 WB Cloud 的 from().select()/insert()/upsert()/update()/delete()，
 *      返回与 fetch 兼容的 { ok, status, json() }，页面无感。
 *   3) 屏蔽 Supabase Realtime WebSocket（WB Cloud 无此通道，靠页面自带 5s 轮询刷新）。
 *
 * 表映射（与 Supabase 同名，WB Cloud 首写自动建集合）：
 *   course_stats  —— 每课自评/评分统计（一课一行，按 course_id 去重）
 *   course_notes  —— 错误原因 + 标签笔记
 * ========================================================================= */
(function () {
  'use strict';

  var WB_CLOUD_CFG = {
    endpoint: 'https://jikaka-memory.app.workbuddy.host',
    publishableKey: 'wbpk_QuSSvKgXD7uP73LA5D5gNT_W0t84UkhE7UB0e9poO19fS9ZgJR6WlOP'
  };
  window.WB_CLOUD_CFG = WB_CLOUD_CFG;
  window.WB_READY = false;
  window.WB_DB = null;

  /* ---------- 1) SDK 载入 ---------- */
  (function loadSdk() {
    var srcs = [
      'https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js',
      'https://unpkg.com/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js'
    ];
    var i = 0;
    (function next() {
      if (typeof WorkBuddyCloud !== 'undefined') { initClient(); return; }
      if (i >= srcs.length) { window.__WB_SDK_FAIL = true; return; }
      var s = document.createElement('script');
      s.src = srcs[i++];
      s.onload = function () { if (typeof WorkBuddyCloud === 'undefined') { next(); } else { initClient(); } };
      s.onerror = function () { next(); };
      (document.head || document.documentElement).appendChild(s);
    })();
  })();

  function initClient() {
    try {
      var client = WorkBuddyCloud.createWorkBuddyCloud({
        endpoint: WB_CLOUD_CFG.endpoint,
        publishableKey: WB_CLOUD_CFG.publishableKey
      });
      window.WB_DB = client.database;
      window.WB_READY = true;
    } catch (e) { window.__WB_SDK_FAIL = true; }
  }

  /* ---------- 2) 翻译层 ---------- */
  // 知识页 Supabase 表名 → WB Cloud 表名 映射（同源 jikaka-memory 后端）
  //   tape_stats → knowledge  (导航统计：fig_id 主键)
  //   tape_state → tape_state (胶带遮盖上 layered 状态：fig_id 主键, state jsonb)
  // 课件库表(course_stats/course_notes)不在此映射，走原 courseware 逻辑
  var KNOWLEDGE_TABLE_MAP = { tape_stats: 'knowledge', tape_state: 'tape_state' };

  function waitWbReady(ms) {
    ms = ms || 12000;
    return new Promise(function (resolve) {
      if (window.WB_DB) return resolve(true);
      var n = 0, step = 200, max = Math.ceil(ms / step);
      var t = setInterval(function () {
        if (window.WB_DB) { clearInterval(t); return resolve(true); }
        if (window.__WB_SDK_FAIL || ++n >= max) { clearInterval(t); return resolve(false); }
      }, step);
    });
  }

  function makeResp(data, status) {
    wbBadge(status);
    return {
      ok: (status >= 200 && status < 300),
      status: status || 200,
      json: function () { return Promise.resolve(data); }
    };
  }

  /* 右下角云状态角标：让用户即时看到写库是否成功（跨域拦截会立刻显现） */
  function showCloudBadge(state, detail) {
    try {
      var el = document.getElementById('wbCloudBadge');
      if (!el) {
        el = document.createElement('div');
        el.id = 'wbCloudBadge';
        el.style.cssText = 'position:fixed;right:10px;bottom:10px;z-index:99999;font:12px/1.5 system-ui,-apple-system,sans-serif;padding:6px 11px;border-radius:9px;box-shadow:0 2px 10px rgba(0,0,0,.18);max-width:260px;pointer-events:none;transition:opacity .3s';
        (document.body || document.documentElement).appendChild(el);
      }
      if (state === 'ok') { el.style.background = '#E6F4EA'; el.style.color = '#137333'; el.textContent = '☁ 已连接 WB Cloud（写库正常）'; }
      else if (state === 'wait') { el.style.background = '#FEF7E0'; el.style.color = '#B06000'; el.textContent = '☁ 连接云端中…'; }
      else { el.style.background = '#FCE8E8'; el.style.color = '#C5221F'; el.textContent = '⚠️ 云端写入失败：' + (detail || '可能被跨域拦截，请用 CloudStudio 链接打开本页'); }
    } catch (e) {}
  }
  function wbBadge(status) {
    if (status >= 200 && status < 300) showCloudBadge('ok');
    else if (status === 502) showCloudBadge('wait');
    else showCloudBadge('err', status === 500 ? 'WB Cloud 拒绝写入' : 'WB Cloud 未就绪');
  }

  // 把 supabase REST 查询串解析成 WB Cloud 构造器参数
  function parseQuery(search) {
    var cols = '*', eqs = [], order = null, limit = null;
    var params = new URLSearchParams(search);
    params.forEach(function (val, key) {
      if (key === 'select') { cols = val; }
      else if (key === 'order') { var a = val.split('.'); order = { col: a[0], asc: a[1] !== 'desc' }; }
      else if (key === 'limit') { limit = parseInt(val, 10) || null; }
      else {
        var m = val.match(/^(eq|ne|gt|gte|lt|lte|like|ilike|is|in|cs|cd|ov|fts|plfts|phfts|wfts)\.(.*)$/);
        if (m) { eqs.push({ col: key, op: m[1], val: m[2] }); }
        else { eqs.push({ col: key, op: 'eq', val: val }); }
      }
    });
    return { cols: cols, eqs: eqs, order: order, limit: limit };
  }

  function applyFilters(qb, eqs, order, limit) {
    eqs.forEach(function (f) {
      if (f.op === 'eq') qb = qb.eq(f.col, f.val);
      else if (f.op === 'in') { var v = f.val.replace(/^\(|\)$/g, '').split(','); qb = qb.in(f.col, v); }
      else if (f.op === 'cs' || f.op === 'cd' || f.op === 'ov') {
        try { qb = qb.contains(f.col, JSON.parse(f.val)); } catch (e) { qb = qb.contains(f.col, f.val); }
      } else qb = qb.filter(f.col, f.op, f.val);
    });
    if (order) qb = qb.order(order.col, { ascending: order.asc });
    if (limit) qb = qb.limit(limit);
    return qb;
  }

  async function wbFetchRest(url, opts) {
    opts = opts || {};
    var method = (opts.method || 'GET').toUpperCase();
    var u; try { u = new URL(url); } catch (e) { return makeResp([], 400); }
    var m = u.pathname.match(/\/rest\/v1\/([^?/]+)/);
    if (!m) return makeResp([], 400);
    var table = m[1];
    var wbTable = KNOWLEDGE_TABLE_MAP[table] || table;
    var isMapped = (KNOWLEDGE_TABLE_MAP[table] != null);
    var q = parseQuery(u.search);
    var ready = await waitWbReady(12000);
    if (!ready || !window.WB_DB) return makeResp([], 502);
    var db = window.WB_DB;
    try {
      if (method === 'GET') {
        var qb = db.from(wbTable).select(q.cols);
        qb = applyFilters(qb, q.eqs, q.order, q.limit);
        var r1 = await qb;
        if (r1.error) return makeResp([], 500);
        return makeResp(r1.data || [], 200);
      } else if (method === 'POST') {
        var rows = JSON.parse(opts.body || '[]');
        if (!Array.isArray(rows)) rows = [rows];
        var prefer = ((opts.headers && (opts.headers.Prefer || opts.headers.prefer)) || '').toString();
        // 知识页映射表（tape_stats/tape_state）：按 fig_id 主键 upsert
        // （Block C 的 Prefer 拼写 'merge-duplications' 不含 'merge-duplicates'，这里强制 upsert 兜底）
        if (isMapped) {
          var r2 = await db.from(wbTable).upsert(rows, { onConflict: 'fig_id' });
          if (r2.error) return makeResp([], 500);
          return makeResp(r2.data || [], 201);
        }
        if (/merge-duplicates/.test(prefer)) {
          // course_stats：按 course_id 一课一行 → 用 id 去重（WB Cloud upsert 按 id）
          rows.forEach(function (row) {
            if (row && row.course_id != null && row.id == null) row.id = String(row.course_id);
          });
          var r2b = await db.from(wbTable).upsert(rows);
          if (r2b.error) return makeResp([], 500);
          return makeResp(r2b.data || [], 201);
        } else {
          // course_notes：每条独立，补 id 保证可插入/可删
          rows.forEach(function (row) {
            if (row && row.id == null) {
              row.id = [row.course_id, row.created_at, row.note, Date.now(), Math.random()]
                .filter(function (x) { return x != null; }).join('|');
            }
          });
          var r3 = await db.from(wbTable).insert(rows);
          if (r3.error) return makeResp([], 500);
          return makeResp(r3.data || [], 201);
        }
      } else if (method === 'DELETE') {
        var qbd = db.from(wbTable).delete();
        qbd = applyFilters(qbd, q.eqs, null, null);
        var r4 = await qbd;
        if (r4.error) return makeResp([], 500);
        return makeResp(r4.data || [], 200);
      } else if (method === 'PATCH' || method === 'PUT') {
        var patch = JSON.parse(opts.body || '{}');
        var qbu = db.from(wbTable).update(patch);
        qbu = applyFilters(qbu, q.eqs, null, null);
        var r5 = await qbu;
        if (r5.error) return makeResp([], 500);
        return makeResp(r5.data || [], 200);
      }
      return makeResp([], 405);
    } catch (e) {
      return makeResp([], 500);
    }
  }

  /* ---------- 3) 拦截 Supabase REST fetch → WB Cloud ---------- */
  if (typeof window.fetch === 'function') {
    var REAL_FETCH = window.fetch.bind(window);
    window.fetch = function (url, opts) {
      if (typeof url === 'string' && /supabase\.co\/rest\/v1\//.test(url)) {
        return wbFetchRest(url, opts);
      }
      return REAL_FETCH(url, opts);
    };
  }

  /* ---------- 4) 屏蔽 Supabase Realtime（WB Cloud 无此通道） ---------- */
  if (typeof window.WebSocket !== 'undefined') {
    var RealWS = window.WebSocket;
    window.WebSocket = function (url, proto) {
      if (typeof url === 'string' && /supabase\.co\/realtime/.test(url)) {
        // 返回永不连接的假 socket，避免无谓重试；数据刷新靠页面自带 5s 轮询
        return {
          close: function () {}, send: function () {},
          onopen: null, onmessage: null, onerror: null, onclose: null,
          readyState: 3, CONNECTING: 0, OPEN: 1, CLOSING: 2, CLOSED: 3
        };
      }
      return new RealWS(url, proto);
    };
    window.WebSocket.prototype = RealWS.prototype;
  }
})();
