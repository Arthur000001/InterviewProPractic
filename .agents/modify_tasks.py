import os
import glob
from bs4 import BeautifulSoup
import re

tasks_dir = "view/tasks"

for filepath in glob.glob(os.path.join(tasks_dir, "task_*.html")):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove stats from sidebar items
    for li in soup.find_all("li", class_="task-item"):
        text = li.get_text()
        # Clean up badge text like 🎯 18 грейд | ⏱️ 2 мин | 📊 35 раз
        text = re.sub(r'🎯.*?(?:мин|раз[а-я]?|\|)\s*(?:\|?\s*📊\s*\d+\s*раз[а-я]?)?', '', text).strip()
        # Keep original onclick, just replace inner HTML but we can't easily do that with beautifulsoup without wiping tags.
        # Actually, sidebar items are just text.
        # Wait, the sidebar item text in task_*.html is currently trimmed anyway.
        # Let's just find the text nodes inside li and clean them.
        for text_node in li.find_all(string=True):
            cleaned = re.sub(r'🎯.*', '', text_node)
            text_node.replace_with(cleaned)

    # Topbar modification
    topbar = soup.find("div", class_="topbar")
    if topbar:
        # Find stats in the main content
        badge = soup.find("span", class_="badge")
        stats_html = ""
        timer_min = 0
        if badge:
            stats_html = str(badge)
            match = re.search(r'⏱️\s*(\d+)\s*мин', badge.get_text())
            if match:
                timer_min = int(match.group(1))
            badge.decompose() # Remove from original location
        
        # We need to restructure topbar
        # Currently topbar has: <div style="...">Задача X</div> and <button>...</button>
        title_div = topbar.find("div")
        if title_div:
            # We add stats to the left side
            left_div = soup.new_tag("div")
            left_div['style'] = "display: flex; align-items: center; gap: 15px;"
            left_div.append(title_div.extract())
            if stats_html:
                stats_soup = BeautifulSoup(stats_html, 'html.parser')
                left_div.append(stats_soup)
            
            # Center timer
            center_div = soup.new_tag("div")
            center_div['style'] = "font-weight: bold; font-size: 1.2rem; color: #ff5b5b;"
            center_div['id'] = "timer-display"
            center_div['data-minutes'] = str(timer_min)
            center_div.string = f"{timer_min:02d}:00" if timer_min > 0 else "00:00"
            
            solve_btn = topbar.find("button", id="solve-btn")
            right_div = soup.new_tag("div")
            if solve_btn:
                right_div.append(solve_btn.extract())
            
            topbar.clear()
            topbar.append(left_div)
            topbar.append(center_div)
            topbar.append(right_div)
    
    # Task content restructuring
    task_content = soup.find("div", id="task-content")
    if task_content:
        summary = task_content.find("summary", class_="question-summary")
        question_text = ""
        if summary:
            q_span = summary.find("span", class_="question-text")
            if q_span:
                question_text = str(q_span.decode_contents())
            summary.decompose()
            
        answer_box = task_content.find("div", class_="answer-box")
        content_html = ""
        if answer_box:
            content_html = str(answer_box.decode_contents())
            answer_box.decompose()
            
        # Clean up the key-question details
        details = task_content.find("details", class_="key-question")
        if details:
            details.decompose()
            
        # Try to split content into description and solution.
        # Often solution starts with <strong>Ответ:</strong>
        description_part = content_html
        solution_part = "<p>Решение не предоставлено</p>"
        
        if "<strong>Ответ:</strong>" in content_html:
            parts = content_html.split("<strong>Ответ:</strong>", 1)
            description_part = parts[0]
            solution_part = "<strong>Ответ:</strong>" + parts[1]
        
        # Build new DOM
        # 1. Description
        desc_div = soup.new_tag("div")
        desc_div['style'] = "margin-bottom: 30px; font-size: 1.1rem; line-height: 1.6;"
        desc_div.append(BeautifulSoup(f"<h3>{question_text}</h3>" + description_part, 'html.parser'))
        
        # 2. Details dropdown
        details_details = soup.new_tag("details")
        details_details['style'] = "margin-bottom: 15px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid var(--border-color);"
        details_summary = soup.new_tag("summary")
        details_summary['style'] = "cursor: pointer; font-weight: bold;"
        details_summary.string = "Детали решения (грейды и т.д.)"
        details_details.append(details_summary)
        details_content = soup.new_tag("div")
        details_content['style'] = "margin-top: 15px; color: var(--text-secondary);"
        details_content.string = "Здесь можно описать примеры, логику оценки по грейдам."
        details_details.append(details_content)
        
        # 3. Solution dropdown
        solution_details = soup.new_tag("details")
        solution_details['style'] = "padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid var(--border-color);"
        solution_summary = soup.new_tag("summary")
        solution_summary['style'] = "cursor: pointer; font-weight: bold;"
        solution_summary.string = "Показать решение"
        solution_details.append(solution_summary)
        solution_content = soup.new_tag("div")
        solution_content['style'] = "margin-top: 15px;"
        solution_content.append(BeautifulSoup(solution_part, 'html.parser'))
        solution_details.append(solution_content)
        
        task_content.append(desc_div)
        task_content.append(details_details)
        task_content.append(solution_details)

    # Timer logic in JS
    js_addition = """
    let timerInterval = null;
    let secondsRemaining = 0;
    
    function startTimer() {
      const display = document.getElementById('timer-display');
      if (!display) return;
      const mins = parseInt(display.getAttribute('data-minutes') || '0', 10);
      if (mins === 0) return;
      
      secondsRemaining = mins * 60;
      clearInterval(timerInterval);
      
      timerInterval = setInterval(() => {
        if (secondsRemaining <= 0) {
          clearInterval(timerInterval);
          return;
        }
        secondsRemaining--;
        const m = Math.floor(secondsRemaining / 60);
        const s = secondsRemaining % 60;
        display.innerText = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
      }, 1000);
    }
    
    function stopTimer() {
      clearInterval(timerInterval);
    }
    """
    
    # Replace toggleCompiler
    old_script = soup.find("script")
    if old_script:
        script_text = old_script.string
        if script_text:
            # We want to add startTimer to toggleCompiler
            script_text = script_text.replace(
                "iframe.src = 'https://go.dev/play/';", 
                "iframe.src = 'https://go.dev/play/';\n        startTimer();"
            )
            script_text = script_text.replace(
                "iframe.src = 'about:blank';",
                "iframe.src = 'about:blank';\n        stopTimer();"
            )
            script_text += js_addition
            old_script.string = script_text
            
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup))
