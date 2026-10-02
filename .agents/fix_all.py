import os, glob, re, json

# Extract stats mapping from transcript_full.jsonl
transcript_path = "/home/interviewer/.gemini/antigravity-ide/brain/7f2948eb-64c4-477d-8a0f-ff5c1de2c8b0/.system_generated/logs/transcript_full.jsonl"
stats_map = {}

# Known from memory
stats_map[1] = "🎯 20 грейд | ⏱️ 5 мин | 📊 18 раз"
stats_map[2] = "🎯 18 грейд | ⏱️ 2 мин | 📊 35 раз"

try:
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            if "nav-task-" in line and "🎯" in line:
                data = json.loads(line)
                content = data.get("content", "")
                
                # Find all list items
                for match in re.finditer(r'<li class="task-item" id="nav-task-(\d+)"[^>]*>([\s\S]*?)</li>', content):
                    task_id = int(match.group(1))
                    li_content = match.group(2)
                    stats_match = re.search(r'🎯[^\n<]+', li_content)
                    if stats_match:
                        stats = stats_match.group(0).strip()
                        # Clean trailing dots if any, but they might be truncated.
                        stats_map[task_id] = stats
except Exception as e:
    print("Error reading transcript:", e)

print("Recovered stats for tasks:", sorted(stats_map.keys()))

tasks_dir = "view/tasks"
for filepath in glob.glob(os.path.join(tasks_dir, "task_*.html")):
    task_id = int(re.search(r'task_(\d+)\.html', filepath).group(1))
    
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # Get stats for this task
    stats = stats_map.get(task_id, "")
    timer_mins = 5
    timer_match = re.search(r'⏱️\s*(\d+)', stats)
    if timer_match:
        timer_mins = int(timer_match.group(1))
        
    # --- FIX 1: Body and layout CSS ---
    # Make sure html, body has height 100% and margin 0
    if "<style>" in html:
        html = re.sub(r'<style>', '<style>\n    html, body { margin: 0; padding: 0; height: 100%; width: 100%; }\n', html)
    
    # Ensure tasks-layout fills the screen
    html = re.sub(r'\.tasks-layout\s*\{[^}]*\}', 
                  '.tasks-layout {\n      display: flex;\n      flex-direction: row;\n      height: 100vh;\n      width: 100vw;\n      overflow: hidden;\n    }', html)
                  
    # --- FIX 3: Topbar Layout ---
    topbar_css = """
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 15px 40px;
      border-bottom: 1px solid var(--border-color);
      background: var(--bg-secondary);
      width: 100%;
      box-sizing: border-box;
    }
    .topbar > div {
      flex: 1;
      display: flex;
    }
    """
    html = re.sub(r'\.topbar\s*\{[^}]*\}', topbar_css, html)
    
    # Rebuild topbar HTML
    badge_html = f'<span class="badge" style="background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.35); font-size: 0.75rem; padding: 3px 8px; border-radius: 4px; margin-left: 12px; white-space: nowrap;">{stats}</span>' if stats else ''
    
    new_topbar = f"""<div class="topbar">
        <div style="align-items: center; justify-content: flex-start;">
            <div style="font-weight: bold; color: var(--text-primary); font-size: 1.1rem;">Задача {task_id}</div>
            {badge_html}
        </div>
        <div style="justify-content: center; align-items: center;">
            <div id="timer-display" data-minutes="{timer_mins}" style="font-weight: bold; font-size: 1.3rem; color: #ff5b5b;">{timer_mins:02d}:00</div>
        </div>
        <div style="justify-content: flex-end; align-items: center;">
            <button id="solve-btn" class="solve-btn" style="margin-bottom: 0;" onclick="toggleCompiler()">💻 Решать задачу</button>
        </div>
      </div>"""
      
    html = re.sub(r'<div class="topbar".*?</div>\s*<div class="task-content"', new_topbar + '\n      <div class="task-content"', html, flags=re.DOTALL)
    
    # --- FIX 4: Answer Box separation ---
    # We need to make sure the solution is actually hidden.
    # Look at the content inside task-content
    # The previous script might have left everything in description_part.
    content_match = re.search(r'<div class="task-content" id="task-content">(.*?)<div class="compiler-split"', html, re.DOTALL)
    if content_match:
        content_html = content_match.group(1)
        
        # We want to extract the task description + code block as QUESTION.
        # And everything that follows (like "Ответ:", "Решение:", or other text) as SOLUTION.
        # If there is no clear delimiter, we will look for <p>Ответ:</p> or <strong>Ответ:</strong>
        
        # In the original structure, a lot of things were lumped together.
        # Let's try to parse the original HTML from the file if we can't find a clean separation.
        # Since we already ran a regex on it, let's fix it by parsing the current content.
        
        # We know there's a `<div style="margin-bottom: 30px;` block containing the description.
        # And then `<details>` blocks.
        
        # We will try to find "Ответ" or "Решение" and push it to the details.
        
        # If the user complains that "сразу и решение и задача", it means the description block contains the answer text.
        desc_block_match = re.search(r'<div style="margin-bottom: 30px;[^>]*>(.*?)</div>\s*<details', content_html, re.DOTALL)
        if desc_block_match:
            inner_desc = desc_block_match.group(1)
            
            # Split point: "Ответ", "Решение", or the first paragraph that isn't a code block.
            # Actually, looking at topic_03_go_practice.html, the answers usually start with:
            # <p><strong>Ответ:</strong> ...
            # Let's try to split by <p><strong>Ответ:</strong>
            
            split_points = [r'<p><strong>Ответ:</strong>', r'<strong>Ответ:</strong>', r'Ответ:']
            
            question_part = inner_desc
            answer_part = "<p>Решение не предоставлено</p>"
            
            for sp in split_points:
                match = re.search(f'({sp}.*)', inner_desc, re.IGNORECASE | re.DOTALL)
                if match:
                    question_part = inner_desc[:match.start()]
                    answer_part = match.group(1)
                    break
                    
            # Re-assemble
            new_content = f"""
        <div style="margin-bottom: 30px; font-size: 1.1rem; line-height: 1.6;">
            {question_part}
        </div>
        
        <details style="margin-bottom: 15px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid var(--border-color);">
            <summary style="cursor: pointer; font-weight: bold; font-size: 1.05rem;">Детали решения (грейды и нюансы)</summary>
            <div style="margin-top: 15px; color: var(--text-secondary);">
                Здесь можно описать примеры, логику оценки по грейдам, если она есть.
            </div>
        </details>
        
        <details style="padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid var(--border-color);">
            <summary style="cursor: pointer; font-weight: bold; font-size: 1.05rem;">Показать решение</summary>
            <div style="margin-top: 15px;">
                {answer_part}
            </div>
        </details>
"""
            html = html.replace(content_html, new_content + "\n      ")
            
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
