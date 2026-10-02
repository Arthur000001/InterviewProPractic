import os
import re

tasks_dir = '/home/interviewer/Projects/InterviewProPractic/view/tasks'

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update the sidebar to just say "Задача 1", "Задача 2", etc.
    # We find all <li class="task-item" id="nav-task-X" ...>...</li>
    # and replace the content with "Задача X"
    def repl_sidebar(m):
        task_id = m.group(1)
        return f'<li class="task-item" id="nav-task-{task_id}" onclick="window.location.href=\'task_{int(task_id):02d}.html\'">Задача {task_id}</li>'
    
    content = re.sub(r'<li class="task-item" id="nav-task-(\d+)"[^>]*>.*?</li>', repl_sidebar, content, flags=re.DOTALL)

    # 2. Fix the description area.
    # Currently it looks like:
    # <h3><strong>28.</strong> Разработчик дал на ревью...</h3>
    # <div style="margin: 12px 0 16px 0;"><p>...</p>
    # <pre><code>...</code></pre>
    
    # We want to find the task-content div:
    # <div class="task-content" id="task-content"> ... </div>
    
    # First, let's remove the <h3><strong>...</strong> completely, and extract its text.
    h3_match = re.search(r'<h3>(?:<strong>.*?</strong>\s*)?(.*?)</h3>', content)
    if h3_match:
        h3_text = h3_match.group(1).strip()
        # Replace the h3 with a nice paragraph
        content = re.sub(r'<h3>(?:<strong>.*?</strong>\s*)?.*?</h3>', f'<p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 15px; color: var(--text-primary);">{h3_text}</p>', content)

    # Next, we wrap the <pre><code ...> ... </code></pre> in a details block.
    # We find <pre><code ... </pre> and replace it.
    def repl_code(m):
        code_html = m.group(0)
        # Wrap in a nicely styled details block
        return f'''<details style="margin-bottom: 15px; padding: 15px; background: #1e1e1e; border-radius: 8px; border: 1px solid #333;">
            <summary style="cursor: pointer; font-weight: bold; font-size: 1.05rem; color: #fff;">💻 Исходный код задачи</summary>
            <div style="margin-top: 15px; position: relative;">
                {code_html}
            </div>
        </details>'''
        
    # Wait, the add_copy.js logic relies on <pre>. The new details block will contain the <pre>.
    # So we just wrap <pre>...</pre>
    if '<details style="margin-bottom: 15px; padding: 15px; background: #1e1e1e;' not in content:
        content = re.sub(r'<pre><code class="language-go">.*?</code></pre>', repl_code, content, flags=re.DOTALL)

    # Clean up any leftover <div><p> and empty <div> around the description, but let's be careful not to break layout.
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for i in range(1, 23):
    filepath = os.path.join(tasks_dir, f'task_{i:02d}.html')
    if os.path.exists(filepath):
        process_file(filepath)

print("Done refactoring HTML files.")
