/* ===== 📌 课件训练进度断点（2026-10-03 方案C：本地实时 + 云端备份） =====
 * 与 tnav 串联导航配合：URL 带 ?tr=<序号> 且 train_group.rid 存在时，
 * 每次打开/切课记录「该队列练到第几课」——本地 localStorage（wulun_tp_cw）
 * + 云端 practice_sessions.progress（经 WB Cloud 适配器写入，跨设备）。
 * app 端 startPracticeSession 课件分支读断点 → 直接跳上次练到的课。 */
(function(){
  'use strict';
  if (window.__cwTp) return;
  window.__cwTp = true;
  var SUPA = 'https://mixuqjognbdrafrrlivc.supabase.co/rest/v1/';   /* 由 WB Cloud 适配器透明翻译 */
  function getQ(k){
    try{ var v = new URLSearchParams(location.search).get(k); if(v != null) return v; }catch(e){}
    var m = location.search.match(new RegExp('[?&]' + k + '=([^&]+)'));
    return m ? decodeURIComponent(m[1]) : null;
  }
  var ti = parseInt(getQ('tr'), 10);
  if (isNaN(ti) || ti < 0) return;
  var g = null;
  try { g = JSON.parse(localStorage.getItem('train_group')); } catch(e){}
  if (!g || !g.urls || !g.urls.length) return;
  var rid = getQ('q') || g.rid || null;
  if (!rid) return;   /* 非队列串联（如门户自选课件组）不记断点 */
  var total = g.urls.length;
  var LS = 'wulun_tp_cw';

  function localSave(rec){
    var all = {};
    try{ all = JSON.parse(localStorage.getItem(LS) || '{}'); }catch(e){}
    if(rec) all[rid] = rec; else delete all[rid];
    try{ localStorage.setItem(LS, JSON.stringify(all)); }catch(e){}
  }
  function cloudSave(rec){
    /* 读-合-写：先取整行再 upsert，避免部分列被覆盖 */
    fetch(SUPA + 'practice_sessions?rid=eq.' + encodeURIComponent(rid) + '&select=rid,title,subject,source,card_ids,new_card_ids,hit_map,browsed_at&limit=1', { headers: {'Content-Type':'application/json'} })
      .then(function(r){ return r.ok ? r.json() : []; })
      .then(function(a){
        var s = (a && a[0]) || null;
        var row = s ? JSON.parse(JSON.stringify(s)) : { rid: rid, title: '', subject: '跨科', source: 'courseware-portal', card_ids: [], new_card_ids: [], hit_map: {} };
        row.progress = rec;
        row.browsed_at = new Date().toISOString();
        return fetch(SUPA + 'practice_sessions?on_conflict=rid', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Prefer': 'resolution=merge-duplicates,return=minimal' },
          body: JSON.stringify([row])
        });
      })
      .catch(function(){ /* 断点备份失败不影响训练 */ });
  }
  var rec = { kind: 'cw', idx: ti, total: total, ts: Date.now() };
  localSave(rec);
  cloudSave(rec);
})();
