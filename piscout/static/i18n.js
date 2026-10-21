/* 介面語言：自動偵測，也可以手動切換。
 *
 * 介面文字原本就是用繁體中文寫的（中文是原文），其他語言是在畫面上把中文換掉。
 * 翻譯不在這支程式裡，放在 static/locales/<語言代碼>.json，由 /i18n-data.js 交給這裡。
 * 想新增語言只要放一個語言檔進去，不用改程式，做法見 docs/TRANSLATING.md。
 *
 * 每個語言檔的 ui 有三種規則：
 *   exact  整段文字完全相同才換（短詞用，避免誤傷）
 *   sub    文字中出現就換（長句與固定片語，由長到短）
 *   rx     含數字或變數的句型：{pattern, replace}，replace 裡 $1 $2 是抓到的內容，
 *          {{2}} 是「把抓到的第 2 段也翻譯一遍」
 * 某句這個語言沒翻的話，先用英文，英文也沒有才顯示中文。
 * 後端回傳的錯誤訊息已經依 X-Lang 翻好，不會經過這裡。
 */
(function () {
  const LOCALES = window.PISCOUT_LOCALES || {};
  const SOURCE = 'zh';
  const available = [{code: SOURCE, name: '繁體中文'}].concat(
    Object.keys(LOCALES).map(code => ({code, name: LOCALES[code].name || code})));
  window.PISCOUT_LANGS = available;

  const has = code => code === SOURCE || Object.prototype.hasOwnProperty.call(LOCALES, code);

  function detect() {
    const prefs = (navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || 'en']);
    for (const raw of prefs) {
      const tag = String(raw).toLowerCase();
      if (has(tag)) return tag;
      if (tag.startsWith('zh')) return SOURCE;
      const base = tag.split('-')[0];
      if (has(base)) return base;
    }
    return has('en') ? 'en' : SOURCE;
  }

  const saved = (() => { try { return localStorage.getItem('piscout_lang'); } catch (e) { return null; } })();
  const lang = saved && has(saved) ? saved : detect();
  window.PISCOUT_LANG = lang;
  document.documentElement.lang = lang === SOURCE ? 'zh-Hant' : lang;

  window.setLang = function (l) {
    try { localStorage.setItem('piscout_lang', l); } catch (e) {}
    location.reload();
  };

  // 這個語言的規則，沒翻的部分用英文補上
  function rules() {
    const own = (LOCALES[lang] && LOCALES[lang].ui) || {};
    const en = lang === 'en' ? {} : ((LOCALES.en && LOCALES.en.ui) || {});
    const exact = Object.assign({}, en.exact || {});
    for (const [zh, tr] of Object.entries(own.exact || {})) { if (tr) exact[zh] = tr; }   // 空的 = 還沒翻，保留英文
    const seen = new Set();
    const sub = [];
    for (const [zh, tr] of (own.sub || []).concat(en.sub || [])) {
      if (!seen.has(zh) && tr) { seen.add(zh); sub.push([zh, tr]); }
    }
    sub.sort((a, b) => b[0].length - a[0].length);
    const rx = [];
    for (const r of (own.rx || []).concat(en.rx || [])) {
      try { rx.push([new RegExp(r.pattern), String(r.replace == null ? '' : r.replace)]); } catch (e) { /* 壞掉的規則略過 */ }
    }
    return {exact, sub, rx};
  }
  const R = lang === SOURCE ? null : rules();

  function expand(template, m) {
    return template
      .replace(/\{\{(\d)\}\}/g, (_, i) => trText(m[Number(i)] || ''))
      .replace(/\$(\d)/g, (_, i) => (m[Number(i)] == null ? '' : m[Number(i)]));
  }

  function trText(s) {
    if (!R) return s;
    const norm = s.replace(/\s+/g, ' ').trim();
    if (!/[一-鿿]/.test(norm)) return s;
    let out = norm;
    if (Object.prototype.hasOwnProperty.call(R.exact, out) && R.exact[out]) {
      out = R.exact[out];
    } else {
      for (const [re, template] of R.rx) {
        const m = re.exec(out);
        if (m) out = out.replace(re, (...args) => expand(template, args.slice(0, m.length)));
      }
      for (const [zh, tr] of R.sub) {
        if (out.includes(zh)) out = out.split(zh).join(tr);
      }
    }
    const lead = s.match(/^\s*/)[0], trail = s.match(/\s*$/)[0];
    return lead + out + trail;
  }
  window.t = trText;

  if (!R) return;

  function walk(node) {
    if (node.nodeType === 3) {
      const v = trText(node.nodeValue);
      if (v !== node.nodeValue) node.nodeValue = v;
      return;
    }
    if (node.nodeType !== 1) return;
    if (node.tagName === 'SCRIPT' || node.tagName === 'STYLE') return;
    for (const a of ['placeholder', 'title']) {
      if (node.hasAttribute && node.hasAttribute(a)) {
        const v = trText(node.getAttribute(a));
        if (v !== node.getAttribute(a)) node.setAttribute(a, v);
      }
    }
    for (const c of node.childNodes) walk(c);
  }

  function start() {
    walk(document.body);
    new MutationObserver(muts => {
      for (const m of muts) {
        if (m.type === 'characterData') walk(m.target);
        else if (m.type === 'attributes') walk(m.target);
        else m.addedNodes.forEach(walk);
      }
    }).observe(document.body, {
      subtree: true, childList: true, characterData: true,
      attributes: true, attributeFilter: ['placeholder', 'title'],
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
