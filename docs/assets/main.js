/* XAMPHP site behaviour: highlighter, copy buttons, menus, docs sections. No dependencies. */
(function () {
  "use strict";
  document.documentElement.classList.add("js");

  /* ---------- 1. Tiny syntax highlighter ---------- */
  var STR = "\"(?:\\\\.|[^\"\\\\\\n])*\"|'[^'\\n]*'";
  var LANGS = {
    bash: [
      ["c", "#[^\\n]*"], ["s", STR],
      ["o", "(?<![\\w-])--?[A-Za-z][\\w-]*"],
      ["f", "\\b(?:pip|xamphp|cd|git|python|clight|php|set|echo|copy)\\b"],
      ["n", "\\b\\d+(?:\\.\\d+)*\\b"], ["x", "[|&;<>(){}\\\\]"]
    ],
    json: [
      ["p", "\"(?:\\\\.|[^\"\\\\\\n])*\"(?=\\s*:)"], ["s", "\"(?:\\\\.|[^\"\\\\\\n])*\""],
      ["n", "-?\\b\\d+(?:\\.\\d+)?\\b"], ["k", "\\b(?:true|false|null)\\b"], ["x", "[{}\\[\\],:]"]
    ],
    js: [
      ["c", "\\/\\/[^\\n]*|\\/\\*[\\s\\S]*?\\*\\/"], ["s", STR + "|`[^`]*`"],
      ["k", "\\b(?:const|let|var|function|return|if|else|for|while|new|import|from|export|async|await|class|try|catch)\\b"],
      ["n", "\\b\\d+(?:\\.\\d+)?\\b"], ["f", "\\b[A-Za-z_$][\\w$]*(?=\\()"], ["x", "[{}()\\[\\];,.:=<>!+\\-*\\/&|?]"]
    ],
    py: [
      ["c", "#[^\\n]*"], ["s", "\"\"\"[\\s\\S]*?\"\"\"|" + STR],
      ["k", "\\b(?:def|class|import|from|return|if|elif|else|for|while|in|not|and|or|try|except|finally|with|as|pass|True|False|None|self)\\b"],
      ["n", "\\b\\d+(?:\\.\\d+)?\\b"], ["f", "\\b[A-Za-z_]\\w*(?=\\()"], ["x", "[{}()\\[\\];,.:=<>!+\\-*\\/]"]
    ],
    yaml: [
      ["c", "#[^\\n]*"], ["s", STR], ["p", "^[ \\t-]*[\\w.\\-]+(?=:)"],
      ["n", "\\b\\d+(?:\\.\\d+)?\\b"], ["k", "\\b(?:true|false|null|yes|no)\\b"], ["x", "[:\\-\\[\\]{},]"]
    ],
    kotlin: [
      ["c", "\\/\\/[^\\n]*|\\/\\*[\\s\\S]*?\\*\\/"], ["s", STR], ["t", "@\\w+"],
      ["k", "\\b(?:fun|val|var|class|object|if|else|when|for|while|return|import|package|override|private|public|null|true|false)\\b"],
      ["n", "\\b\\d+(?:\\.\\d+)?\\b"], ["f", "\\b[A-Za-z_]\\w*(?=\\()"], ["x", "[{}()\\[\\];,.:=<>!+\\-*\\/]"]
    ],
    http: [
      ["k", "^(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\\b"], ["t", "HTTP\\/[\\d.]+"],
      ["p", "^[A-Za-z-]+(?=:)"], ["s", STR], ["n", "\\b\\d+\\b"], ["x", "[:\\/?&=]"]
    ],
    apache: [
      ["c", "#[^\\n]*"], ["s", STR], ["t", "<\\/?[A-Za-z]+|>"],
      ["k", "^[ \\t]*(?:DocumentRoot|ServerName|AllowOverride|Require|Listen|Options)\\b"],
      ["o", "\\b(?:All|None|all|granted|denied)\\b"], ["n", "\\*:\\d+|\\b\\d+\\b"]
    ],
    text: []
  };
  var ALIAS = { sh: "bash", shell: "bash", cmd: "bash", javascript: "js", python: "py", kt: "kotlin", yml: "yaml", conf: "apache" };
  var COMPILED = {};

  function esc(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  function compile(lang) {
    if (COMPILED[lang]) return COMPILED[lang];
    var rules = LANGS[lang] || [];
    if (!rules.length) return (COMPILED[lang] = null);
    var re = new RegExp(rules.map(function (r) { return "(" + r[1] + ")"; }).join("|"), "gm");
    return (COMPILED[lang] = { re: re, rules: rules });
  }

  function highlight(src, lang) {
    lang = ALIAS[lang] || lang;
    var c = compile(lang);
    if (!c) return esc(src);
    var out = "", last = 0, m;
    c.re.lastIndex = 0;
    while ((m = c.re.exec(src))) {
      if (m[0] === "") { c.re.lastIndex++; continue; }
      var idx = 0;
      for (var i = 1; i < m.length; i++) { if (m[i] !== undefined) { idx = i - 1; break; } }
      out += esc(src.slice(last, m.index)) + '<span class="tok-' + c.rules[idx][0] + '">' + esc(m[0]) + "</span>";
      last = m.index + m[0].length;
    }
    return out + esc(src.slice(last));
  }

  function copyText(text, btn) {
    function done() {
      var label = btn.querySelector(".lbl");
      btn.classList.add("done");
      if (label) label.textContent = "Copied";
      setTimeout(function () { btn.classList.remove("done"); if (label) label.textContent = "Copy"; }, 1800);
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else { fallback(); }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text; ta.setAttribute("readonly", ""); ta.style.cssText = "position:fixed;opacity:0;top:0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); done(); } catch (e) { /* ignore */ }
      document.body.removeChild(ta);
    }
  }

  function enhanceCode() {
    var blocks = document.querySelectorAll("pre > code[data-lang]");
    Array.prototype.forEach.call(blocks, function (code) {
      var pre = code.parentNode, raw = code.textContent.replace(/^\n+|\s+$/g, ""), lang = code.getAttribute("data-lang");
      var title = code.getAttribute("data-title") || lang;
      try { code.innerHTML = highlight(raw, lang); } catch (e) { code.textContent = raw; }
      pre.setAttribute("tabindex", "0");
      var wrap = document.createElement("div");
      wrap.className = "code";
      var bar = document.createElement("div");
      bar.className = "code-bar";
      bar.innerHTML = '<i></i><i></i><i></i><span></span><button type="button" class="copy" aria-label="Copy code">' +
        '<svg class="icon" aria-hidden="true"><use href="#i-copy"/></svg><span class="lbl">Copy</span></button>';
      bar.querySelector("span").textContent = title;
      bar.querySelector(".copy").addEventListener("click", function () { copyText(raw, this); });
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(bar); wrap.appendChild(pre);
    });
  }

  /* ---------- 2. Burger menu (full-screen overlay) ---------- */
  var root = document.documentElement;
  function closeMenu() {
    var b = document.querySelector(".burger");
    root.classList.remove("menu-open");
    if (b) { b.setAttribute("aria-expanded", "false"); b.setAttribute("aria-label", "Open menu"); }
    var u = b && b.querySelector("use"); if (u) u.setAttribute("href", "#i-menu");
  }
  window.XH_closeMenu = closeMenu;

  function initMenu() {
    var b = document.querySelector(".burger");
    if (!b) return;
    b.addEventListener("click", function () {
      var open = !root.classList.contains("menu-open");
      if (!open) { closeMenu(); return; }
      root.classList.add("menu-open");
      b.setAttribute("aria-expanded", "true"); b.setAttribute("aria-label", "Close menu");
    });
    var panel = document.getElementById(b.getAttribute("aria-controls"));
    if (panel) panel.addEventListener("click", function (e) { if (e.target.closest("a")) closeMenu(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeMenu(); });
    window.addEventListener("resize", function () { if (window.innerWidth > 820) closeMenu(); });
  }

  /* ---------- 3. Docs section switching ---------- */
  function initDocs() {
    var sections = document.querySelectorAll(".doc-section");
    if (!sections.length) return;
    var links = document.querySelectorAll(".docs-nav a[data-section]");
    var siteName = (document.title.split(" | ").pop() || "").trim();
    var ids = Array.prototype.map.call(sections, function (s) { return s.id; });

    function show(id, push) {
      if (ids.indexOf(id) < 0) id = ids[0];
      Array.prototype.forEach.call(sections, function (s) { s.classList.toggle("active", s.id === id); });
      Array.prototype.forEach.call(links, function (a) {
        if (a.getAttribute("data-section") === id) a.setAttribute("aria-current", "true");
        else a.removeAttribute("aria-current");
      });
      var h1 = document.querySelector("#" + id + " h1");
      document.title = (h1 ? h1.textContent : id) + (siteName ? " | " + siteName : "");
      if (push) history.pushState({ id: id }, "", "#" + id);
      window.scrollTo(0, 0);
      closeMenu();
    }

    function fromHash() { return decodeURIComponent(location.hash.replace(/^#/, "")); }
    document.addEventListener("click", function (e) {
      var t = e.target.closest("[data-section],[data-goto]");
      if (!t) return;
      var id = t.getAttribute("data-section") || t.getAttribute("data-goto");
      e.preventDefault();
      show(id, true);
    });
    window.addEventListener("popstate", function () { show(fromHash(), false); });
    show(fromHash(), false);
    setTimeout(function () { window.scrollTo(0, 0); }, 0);
  }

  document.addEventListener("DOMContentLoaded", function () {
    enhanceCode();
    initMenu();
    initDocs();
  });
})();
