import os
import glob
import re
import json
import difflib
import html
import subprocess

with open("/home/interviewer/Projects/InterviewProPractic/.agents/extracted_tasks.json", "r", encoding="utf-8") as f:
    extracted_tasks = json.load(f)

task_files = glob.glob("/home/interviewer/Projects/InterviewProPractic/view/tasks/task_*.html")

def normalize(text):
    if not text: return ""
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#x27;", "'")
    return re.sub(r'\s+', '', text).lower()

def format_go_code(code_str):
    if not code_str:
        return ""
    
    lines = code_str.split('\n')
    text_lines = []
    go_lines = []
    
    in_go = False
    for line in lines:
        if not in_go and re.match(r'^\s*(package|import|func|type|var|const|//)', line):
            in_go = True
        
        if in_go:
            go_lines.append(line)
        else:
            text_lines.append(line)
            
    if not go_lines:
        text_lines = []
        go_lines = lines
        
    raw_go = html.unescape('\n'.join(go_lines))
    
    try:
        res = subprocess.run(['gofmt'], input=raw_go.encode('utf-8'), capture_output=True)
        if res.returncode == 0:
            fmt_go = res.stdout.decode('utf-8')
            fmt_go = html.escape(fmt_go)
            
            final_code = '\n'.join(text_lines)
            if text_lines and fmt_go:
                final_code += '\n' + fmt_go
            elif fmt_go:
                final_code = fmt_go
            return final_code
        else:
            return code_str
    except Exception as e:
        return code_str

# Pass 1: Build the task mapping
task_info = {}

for tfile in task_files:
    task_num_match = re.search(r'task_(\d+)\.html', tfile)
    task_num = int(task_num_match.group(1))
    
    with open(tfile, "r", encoding="utf-8") as f:
        content = f.read()
    
    q_match = re.search(r'<p style="font-size: 1.1rem[^>]*>(.*?)</p>', content, re.DOTALL)
    if not q_match:
        q_match = re.search(r'<div style="font-size: 1.15rem[^>]*>(.*?)</div>', content, re.DOTALL)
    if not q_match:
        q_match = re.search(r'<div style="font-size: 1.15rem; line-height: 1.7; margin-bottom: 24px[^>]*>(.*?)</div>', content, re.DOTALL)
    
    if not q_match:
        print(f"No question text found in {tfile}")
        continue
            
    q_text_original = q_match.group(1).strip()
    norm_q = normalize(q_text_original)
    
    best_match = None
    best_ratio = 0
    for et in extracted_tasks:
        et_norm = normalize(et['question'])
        ratio = difflib.SequenceMatcher(None, norm_q, et_norm).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = et
            
    if best_ratio < 0.8:
        print(f"No good match found for {tfile} (best ratio: {best_ratio})")
        continue
        
    title = best_match['question']
    title = re.sub(r'<[^>]+>', '', title)
    title = title.strip()
    if len(title) > 35:
        title = title[:32] + "..."
        
    task_info[task_num] = {
        'file': tfile,
        'title': title,
        'match': best_match
    }

# Pass 2: Rebuild files
for task_num in sorted(task_info.keys()):
    info = task_info[task_num]
    tfile = info['file']
    match = info['match']
    
    sidebar_items = ""
    for i in range(1, 23):
        if i in task_info:
            disp_title = f"{i}. {task_info[i]['title']}"
        else:
            disp_title = f"Задача {i}"
            
        active = ' class="task-item active"' if i == task_num else ' class="task-item"'
        sidebar_items += f'        <li{active} id="nav-task-{i}" onclick="window.location.href=\'task_{i:02d}.html\'" title="{disp_title}">{disp_title}</li>\n'

    # --- Code block ---
    code_section = ""
    if match['code']:
        formatted_code = format_go_code(match['code'])
        code_section = f"""<details class="section-details">
            <summary>📄 Исходный код</summary>
            <div class="section-body">
                <div class="code-window">
                    <div class="mac-buttons">
                        <div class="mac-btn mac-close"></div>
                        <div class="mac-btn mac-min"></div>
                        <div class="mac-btn mac-max"></div>
                    </div>
                    <button class="copy-btn" onclick="copyCode(this)">📋 Копировать</button>
                    <pre><code class="language-go">{formatted_code}</code></pre>
                </div>
            </div>
        </details>"""

    # --- Extra text (shown before dropdowns) ---
    extra_text_html = ""
    if match.get('extra_text'):
        extra_text_html = f"""<div style="margin-bottom: 20px; color: var(--text-secondary); line-height: 1.65; font-size: 1rem;">{match['extra_text']}</div>"""

    # --- Criteria / implementation details ---
    criteria_html = match.get('criteria', '') or ''
    criteria_section = ""
    if criteria_html.strip():
        criteria_section = f"""<details class="section-details">
            <summary>🔍 Детали реализации</summary>
            <div class="section-body">
                {criteria_html}
            </div>
        </details>"""

    # --- Answer / solution ---
    answer_html = match.get('answer', '') or ''
    answer_section = ""
    if answer_html.strip():
        answer_section = f"""<details class="section-details">
            <summary>✅ Решение</summary>
            <div class="section-body">
                {answer_html}
            </div>
        </details>"""

    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>InterviewPro | Задача {task_num}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="../../styles/style.css">
  <style>
    html, body {{ margin: 0; padding: 0; height: 100%; width: 100%; }}
    .tasks-layout {{ display: flex; flex-direction: row; height: 100vh; width: 100vw; overflow: hidden; }}
    .tasks-sidebar {{ width: 320px; min-width: 320px; max-width: 320px; background: var(--bg-secondary); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; overflow-y: auto; height: 100vh; flex-shrink: 0; }}
    .tasks-sidebar-header {{ padding: 20px; border-bottom: 1px solid var(--border-color); background: var(--bg-secondary); position: sticky; top: 0; z-index: 10; }}
    .task-list {{ list-style: none; padding: 0; margin: 0; }}
    .task-item {{ padding: 13px 20px; border-bottom: 1px solid var(--border-color); cursor: pointer; transition: background 0.2s; font-size: 0.9rem; line-height: 1.4; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .task-item:hover {{ background: rgba(255,255,255,0.05); }}
    .task-item.active {{ background: var(--accent-primary-alpha); border-left: 4px solid var(--accent-primary); }}
    .task-main {{ flex: 1; display: flex; flex-direction: column; background: var(--bg-primary); overflow-y: auto; min-width: 0; }}
    .task-content {{ padding: 32px 40px; max-width: 860px; width: 100%; box-sizing: border-box; }}
    .solve-btn {{ background: linear-gradient(135deg, #005bff 0%, #00d2ff 100%); color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; font-size: 1rem; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 15px rgba(0,91,255,0.3); transition: transform 0.2s, box-shadow 0.2s; text-decoration: none; }}
    .solve-btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,91,255,0.4); color: white; }}
    .topbar {{ display: flex; align-items: center; justify-content: space-between; padding: 15px 40px; border-bottom: 1px solid var(--border-color); background: var(--bg-secondary); width: 100%; box-sizing: border-box; flex-shrink: 0; }}
    .topbar > div {{ flex: 1; display: flex; }}

    /* Collapsible sections */
    .section-details {{ margin-bottom: 12px; border-radius: 10px; border: 1px solid var(--border-color); overflow: hidden; background: var(--bg-secondary); }}
    .section-details summary {{
      cursor: pointer;
      font-weight: 600;
      font-size: 1rem;
      padding: 14px 20px;
      display: flex;
      align-items: center;
      gap: 10px;
      list-style: none;
      user-select: none;
      transition: background 0.2s;
      color: var(--text-primary);
    }}
    .section-details summary::-webkit-details-marker {{ display: none; }}
    .section-details summary::before {{
      content: '▶';
      font-size: 0.7rem;
      transition: transform 0.2s;
      color: var(--accent-primary);
      flex-shrink: 0;
    }}
    .section-details[open] > summary::before {{
      transform: rotate(90deg);
    }}
    .section-details summary:hover {{ background: rgba(255,255,255,0.05); }}
    .section-body {{
      padding: 16px 20px 20px 20px;
      border-top: 1px solid var(--border-color);
      line-height: 1.65;
      color: var(--text-secondary);
    }}

    /* Code block inside collapsible */
    .code-window {{ background: #1a1a1a; border-radius: 8px; border: 1px solid #2d2d2d; position: relative; overflow-x: auto; box-shadow: 0 4px 12px rgba(0,0,0,0.25); }}
    .code-window pre {{ margin: 0; font-family: 'Consolas', 'Fira Code', 'Courier New', monospace; font-size: 0.92rem; color: #d4d4d4; padding: 14px 20px; }}
    .mac-buttons {{ padding: 10px 15px 0 15px; display: flex; gap: 6px; }}
    .mac-btn {{ width: 12px; height: 12px; border-radius: 50%; }}
    .mac-close {{ background: #ff5f56; }}
    .mac-min {{ background: #ffbd2e; }}
    .mac-max {{ background: #27c93f; }}
    .copy-btn {{
      position: absolute; top: 8px; right: 12px;
      padding: 4px 10px; background: rgba(255,255,255,0.08);
      color: #ccc; border: 1px solid rgba(255,255,255,0.15);
      border-radius: 5px; cursor: pointer; font-size: 0.78rem;
      transition: all 0.2s;
    }}
    .copy-btn:hover {{ background: rgba(255,255,255,0.16); color: #fff; }}
  </style>
</head>
<body>
  <div class="tasks-layout">
    <aside class="tasks-sidebar">
      <div class="tasks-sidebar-header">
        <h2 style="margin: 0; font-size: 1.2rem;">🚀 Задачи</h2>
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 8px;">Всего задач: 22</div>
      </div>
      <ul class="task-list">
{sidebar_items}      </ul>
    </aside>

    <main class="task-main">
      <div class="topbar">
        <div style="align-items: center; justify-content: flex-start;">
            <div style="font-weight: bold; color: var(--text-primary); font-size: 1.1rem;">Задача {task_num}</div>
            <span style="background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.35); font-size: 0.75rem; padding: 3px 8px; border-radius: 4px; margin-left: 12px; white-space: nowrap;">{match['badge']}</span>
        </div>
        <div style="justify-content: center; align-items: center;">
            <div id="timer-display" data-minutes="2" style="font-weight: bold; font-size: 1.3rem; color: #ff5b5b;">02:00</div>
        </div>
        <div style="justify-content: flex-end; align-items: center;">
            <a href="https://go.dev/play/" target="_blank" class="solve-btn">💻 Решать задачу</a>
        </div>
      </div>
      
      <div class="task-content" id="task-content">

        <!-- Описание задачи (всегда видно) -->
        <div style="font-size: 1.15rem; line-height: 1.7; margin-bottom: 24px; color: var(--text-primary); font-weight: 500;">
            {match['question']}
        </div>
        {extra_text_html}

        <!-- Выпадашки -->
        {code_section}
        {criteria_section}
        {answer_section}

      </div>
    </main>
  </div>

  <script>
    function copyCode(btn) {{
      const code = btn.closest('.code-window').querySelector('code');
      if (!code) return;
      navigator.clipboard.writeText(code.innerText).then(() => {{
        const orig = btn.innerText;
        btn.innerText = '✅ Скопировано!';
        btn.style.background = 'rgba(52,211,153,0.2)';
        btn.style.borderColor = '#34d399';
        setTimeout(() => {{
          btn.innerText = orig;
          btn.style.background = 'rgba(255,255,255,0.08)';
          btn.style.borderColor = 'rgba(255,255,255,0.15)';
        }}, 2000);
      }});
    }}

    let timerInterval = null;
    let secondsRemaining = 0;
    function startTimer() {{
      const display = document.getElementById('timer-display');
      if (!display) return;
      const mins = parseInt(display.getAttribute('data-minutes') || '2', 10);
      secondsRemaining = mins * 60;
      if (secondsRemaining <= 0) return;
      clearInterval(timerInterval);
      timerInterval = setInterval(() => {{
        if (secondsRemaining <= 0) {{ clearInterval(timerInterval); return; }}
        secondsRemaining--;
        const m = Math.floor(secondsRemaining / 60);
        const s = secondsRemaining % 60;
        display.innerText = `${{m.toString().padStart(2,'0')}}:${{s.toString().padStart(2,'0')}}`;
      }}, 1000);
    }}
  </script>
</body>
</html>
"""
    with open(tfile, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Rebuilt {tfile} (Matched with {info['title']})")
