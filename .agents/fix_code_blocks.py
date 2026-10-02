import os, glob, re
from bs4 import BeautifulSoup

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

    soup = BeautifulSoup(html, 'html.parser')
    changed = False

    for code_block in soup.find_all("code", class_="language-go"):
        # We only want to process the main question code block, not the answers
        # Usually it's in the first div
        text = code_block.get_text()
        lines = text.split('\n')
        
        # Find the split index
        split_idx = 0
        for i, line in enumerate(lines):
            if is_code_line(line):
                # Wait, if line is empty, it might be between text, but if it's purely ascii it will trigger!
                # Ah, `not re.search(r'[А-Яа-я]', line)` is true for empty string, but we handled `if not line: return False`
                # So empty lines are False, meaning they are considered text until we hit actual code.
                split_idx = i
                break
        else:
            # All lines are text? Or no lines triggered code.
            split_idx = len(lines)
            
        if split_idx > 0 and split_idx < len(lines):
            # We found text before code!
            text_part = '\n'.join(lines[:split_idx]).strip()
            code_part = '\n'.join(lines[split_idx:]).strip()
            
            if text_part:
                changed = True
                
                # Replace the code block content with just the code
                code_block.string = code_part
                
                # Create a new p tag for the text part
                p_tag = soup.new_tag("p")
                p_tag['style'] = "margin-bottom: 15px; color: var(--text-primary);"
                # Replace newlines with <br> for HTML
                p_tag.append(BeautifulSoup(text_part.replace('\n', '<br>'), 'html.parser'))
                
                # Insert before the pre tag
                pre_tag = code_block.parent
                pre_tag.insert_before(p_tag)

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(soup))
