(function () {
  'use strict';

  const LANG_CONFIG = {
    go: {
      label: 'Go',
      color: '#00ADD8',
      run: async function(code) {
        var res = await fetch('https://wandbox.org/api/compile.json', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ compiler: 'go-1.23.2', code: code })
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        var data = await res.json();
        if (data.compiler_error) {
          var cleanErr = data.compiler_error
            .replace(/# _\/home\/wandbox\n\.\/prog\.go:/g, 'строка ')
            .replace(/\.\/prog\.go:/g, 'строка ');
          return { ok: false, output: cleanErr };
        }
        if (data.program_error) {
          var out = (data.program_output ? data.program_output + '\n' : '') + data.program_error;
          return { ok: data.status === '0', output: out };
        }
        return { ok: true, output: data.program_output || '(нет вывода)' };
      }
    }
  };

  function unescapeHtml(str) {
    return str
      .replace(/&amp;/g, '&')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'");
  }

  function createWidget(pre, lang) {
    var config = LANG_CONFIG[lang];
    if (!config) return;

    var codeEl = pre.querySelector('code');
    var originalCode = unescapeHtml(codeEl ? codeEl.textContent : pre.textContent);

    var widget = document.createElement('div');
    widget.style.cssText = 'border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,0.1);margin:20px 0;background:#0f0f1a;box-shadow:0 6px 30px rgba(0,0,0,0.5);';

    var header = document.createElement('div');
    header.style.cssText = 'display:flex;align-items:center;justify-content:space-between;padding:10px 16px;background:rgba(255,255,255,0.04);border-bottom:1px solid rgba(255,255,255,0.08);';
    header.innerHTML = '<span style="font-size:12px;font-weight:700;color:' + config.color + ';letter-spacing:0.06em;font-family:monospace;">◆ ' + config.label + '</span>';

    var btn = document.createElement('button');
    btn.textContent = '▶  Run';
    btn.style.cssText = 'background:linear-gradient(135deg,' + config.color + ',' + config.color + '88);color:white;border:none;border-radius:6px;padding:6px 20px;font-size:13px;font-weight:700;cursor:pointer;transition:all 0.15s;letter-spacing:0.05em;';
    btn.onmouseenter = function() { btn.style.opacity = '0.85'; btn.style.transform = 'scale(1.04)'; };
    btn.onmouseleave = function() { btn.style.opacity = '1'; btn.style.transform = 'scale(1)'; };
    header.appendChild(btn);

    var editor = document.createElement('textarea');
    editor.value = originalCode;
    editor.spellcheck = false;
    editor.style.cssText = 'width:100%;min-height:200px;max-height:500px;background:#0a0a16;color:#e2e8f0;border:none;outline:none;padding:16px;font-family:"JetBrains Mono","Fira Code","Consolas",monospace;font-size:13.5px;line-height:1.7;resize:vertical;box-sizing:border-box;tab-size:4;';
    editor.addEventListener('keydown', function(e) {
      if (e.key === 'Tab') {
        e.preventDefault();
        var s = editor.selectionStart;
        editor.value = editor.value.substring(0, s) + '    ' + editor.value.substring(editor.selectionEnd);
        editor.selectionStart = editor.selectionEnd = s + 4;
      }
    });

    var outputDiv = document.createElement('div');
    outputDiv.style.cssText = 'display:none;padding:14px 16px;background:#070710;border-top:1px solid rgba(255,255,255,0.06);';
    var outputLabel = document.createElement('div');
    outputLabel.textContent = 'OUTPUT';
    outputLabel.style.cssText = 'font-size:10px;color:#555;margin-bottom:8px;letter-spacing:0.1em;font-family:monospace;';
    var resultPre = document.createElement('pre');
    resultPre.style.cssText = 'margin:0;color:#4ade80;font-size:13px;white-space:pre-wrap;word-break:break-word;font-family:"JetBrains Mono",monospace;';
    outputDiv.appendChild(outputLabel);
    outputDiv.appendChild(resultPre);

    btn.addEventListener('click', async function() {
      btn.textContent = '⏳ Компиляция...';
      btn.disabled = true;
      outputDiv.style.display = 'block';
      resultPre.style.color = '#94a3b8';
      resultPre.textContent = 'Отправка кода...';
      try {
        var result = await config.run(editor.value);
        resultPre.style.color = result.ok ? '#4ade80' : '#f87171';
        resultPre.textContent = result.output;
      } catch(e) {
        resultPre.style.color = '#f87171';
        resultPre.textContent = 'Ошибка сети: ' + e.message + '\n\nОткройте сайт через локальный сервер:\n  cd view && npx serve .';
      }
      btn.textContent = '▶  Run';
      btn.disabled = false;
    });

    widget.appendChild(header);
    widget.appendChild(editor);
    widget.appendChild(outputDiv);
    pre.replaceWith(widget);
  }

  function init() {
    document.querySelectorAll('pre > code').forEach(function(codeEl) {
      var cls = codeEl.className || '';
      var m = cls.match(/language-(\w+)/);
      if (!m) return;
      var lang = m[1].toLowerCase();
      if (!LANG_CONFIG[lang]) return;
      createWidget(codeEl.parentElement, lang);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();