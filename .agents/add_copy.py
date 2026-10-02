import os, glob, re

tasks_dir = "view/tasks"
for filepath in glob.glob(os.path.join(tasks_dir, "task_*.html")):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # Add Copy to clipboard logic and button for code blocks
    # We will inject a script at the end of the body to handle copying
    copy_script = """
    <script>
      // Automatically add a copy button to all pre>code blocks
      document.addEventListener('DOMContentLoaded', () => {
        const blocks = document.querySelectorAll('pre');
        blocks.forEach((pre) => {
          pre.style.position = 'relative';
          const btn = document.createElement('button');
          btn.innerText = '📋 Копировать код';
          btn.style.position = 'absolute';
          btn.style.top = '10px';
          btn.style.right = '10px';
          btn.style.padding = '5px 10px';
          btn.style.background = 'rgba(255,255,255,0.1)';
          btn.style.color = '#fff';
          btn.style.border = '1px solid rgba(255,255,255,0.2)';
          btn.style.borderRadius = '4px';
          btn.style.cursor = 'pointer';
          btn.style.fontSize = '0.8rem';
          btn.style.zIndex = '10';
          
          btn.addEventListener('click', () => {
            const code = pre.querySelector('code').innerText;
            navigator.clipboard.writeText(code).then(() => {
              btn.innerText = '✅ Скопировано!';
              setTimeout(() => { btn.innerText = '📋 Копировать код'; }, 2000);
            });
          });
          
          pre.appendChild(btn);
        });
      });
    </script>
    """
    
    if "📋 Копировать код" not in html:
        html = html.replace("</body>", copy_script + "\n</body>")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
