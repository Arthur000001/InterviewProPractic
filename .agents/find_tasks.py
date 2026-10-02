import os
import glob
import re
import json

base_dir = "/home/interviewer/Projects/InterviewProCompany/view"
files = glob.glob(f"{base_dir}/**/*.html", recursive=True)

tasks = []

summary_pattern = re.compile(r'<summary[^>]*>(.*?)</summary>', re.DOTALL)
question_text_pattern = re.compile(r'<span class="question-text"[^>]*>(.*?)</span>', re.DOTALL)
badge_pattern = re.compile(r'<span class="badge"[^>]*>(.*?)</span>', re.DOTALL)
code_pattern = re.compile(r'<pre><code class="language-go">(.*?)</code></pre>', re.DOTALL)
criteria_pattern = re.compile(r'<h4[^>]*>🎯 Критерии ответа по грейдам.*?</h4>(.*)', re.DOTALL)

for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    parts = content.split('<details')
    for part in parts[1:]:
        detail_content = part.split('</details>')[0]
        
        summary_match = summary_pattern.search(detail_content)
        if summary_match:
            summary_html = summary_match.group(1)
            qt_match = question_text_pattern.search(summary_html)
            badge_match = badge_pattern.search(summary_html)
            
            if qt_match:
                qt = qt_match.group(1).strip()
                qt = re.sub(r'<strong>.*?</strong>\s*', '', qt).strip()
                qt = re.sub(r'<[^>]+>', '', qt).strip() # strip remaining html tags
                
                code = ""
                code_match = code_pattern.search(detail_content)
                if code_match:
                    code = code_match.group(1).strip()
                    
                details_html = ""
                crit_match = criteria_pattern.search(detail_content)
                extra_text = ""
                
                if crit_match:
                    details_html = crit_match.group(1).strip()
                    # extract everything before the <h4>
                    before_h4 = detail_content.split('<h4')[0]
                    # strip <summary>
                    before_h4 = before_h4.split('</summary>')[-1]
                    # strip answer-box opening tag
                    before_h4 = re.sub(r'<div class="answer-box"[^>]*>', '', before_h4)
                    if code_match:
                        before_h4 = before_h4.replace(code_match.group(0), "")
                    extra_text = before_h4.strip()
                else:
                    # try to extract everything inside answer-box after the code
                    answer_box = re.search(r'<div class="answer-box"[^>]*>(.*)', detail_content, re.DOTALL)
                    if answer_box:
                        ab_html = answer_box.group(1)
                        if code_match:
                            ab_html = ab_html.replace(code_match.group(0), "")
                        # without h4, we assume it's ALL criteria
                        details_html = ab_html.strip()
                
                tasks.append({
                    "question": qt,
                    "extra_text": extra_text,
                    "code": code,
                    "badge": badge_match.group(1).strip() if badge_match else "",
                    "criteria": details_html,
                    "file": fpath
                })

with open("/home/interviewer/Projects/InterviewProPractic/.agents/extracted_tasks.json", "w", encoding="utf-8") as f:
    json.dump(tasks, f, ensure_ascii=False, indent=2)
