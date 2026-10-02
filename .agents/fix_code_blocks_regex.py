import os, glob, re

tasks_dir = "view/tasks"

def is_code_line(line):
    line = line.strip()
    if not line:
        return False
    
    # Strong code indicators
    if line.startswith(("package ", "import", "func ", "type ", "var ", "const ", "//")):
        return True
        
    # If it contains no Cyrillic characters, it's likely code
    if not re.search(r'[А-Яа-я]', line):
        return True
        
    return False

for filepath in glob.glob(os.path.join(tasks_dir, "task_*.html")):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    changed = False

    def replacer(match):
        global changed
        full_match = match.group(0)
        code_text = match.group(1)
        
        lines = code_text.split('\n')
        split_idx = 0
        for i, line in enumerate(lines):
            if is_code_line(line):
                split_idx = i
                break
        else:
            split_idx = len(lines)
            
        if split_idx > 0 and split_idx < len(lines):
            text_part = '\n'.join(lines[:split_idx]).strip()
            code_part = '\n'.join(lines[split_idx:]).strip()
            
            if text_part:
                changed = True
                text_part_html = text_part.replace('\n', '<br>')
                p_tag = f'<p style="margin-bottom: 15px; color: var(--text-primary); font-size: 1rem;">{text_part_html}</p>'
                
                new_code_block = f'<pre><code class="language-go">{code_part}</code></pre>'
                
                return p_tag + '\n' + new_code_block
                
        return full_match
        
    html = re.sub(r'<pre><code class="language-go">([\s\S]*?)</code></pre>', replacer, html)

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
