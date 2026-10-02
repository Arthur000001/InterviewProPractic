import os
import re

css_content = """
/* ==========================================================================
   Copy Code Button Styles
   ========================================================================== */
pre {
  position: relative;
}

.copy-code-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 8px;
  font-size: 0.75rem;
  font-family: var(--font-sans, "Inter", sans-serif);
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 10;
  opacity: 0;
  pointer-events: none;
}

pre:hover .copy-code-btn,
.copy-code-btn:focus,
.copy-code-btn.copied {
  opacity: 1;
  pointer-events: auto;
}

.copy-code-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #f8fafc;
}

.copy-code-btn.copied {
  background: rgba(16, 185, 129, 0.2);
  border-color: rgba(16, 185, 129, 0.4);
  color: #10b981;
}
"""

js_content = """document.addEventListener('DOMContentLoaded', () => {
  const preElements = document.querySelectorAll('pre');
  preElements.forEach(pre => {
    const codeBlock = pre.querySelector('code');
    if (!codeBlock) return;

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-code-btn';
    copyBtn.innerHTML = 'Скопировать';

    copyBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      const text = codeBlock.innerText;
      navigator.clipboard.writeText(text).then(() => {
        copyBtn.innerHTML = 'Скопировано!';
        copyBtn.classList.add('copied');
        
        setTimeout(() => {
          copyBtn.innerHTML = 'Скопировать';
          copyBtn.classList.remove('copied');
        }, 2000);
      }).catch(err => {
        console.error('Copy failed', err);
      });
    });

    pre.appendChild(copyBtn);
  });
});
"""

workspace = "/media/artur/BEA6-BBCE/InterviewPro"

for root, dirs, files in os.walk(workspace):
    if any(ignore in root for ignore in ['.agents', '.backup', '.git']):
        continue
    
    if 'style.css' in files:
        style_path = os.path.join(root, 'style.css')
        with open(style_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'copy-code-btn' not in content:
            with open(style_path, 'a', encoding='utf-8') as f:
                f.write(css_content)
            print(f"Appended CSS to {style_path}")
            
        js_path = os.path.join(root, 'copy_code.js')
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"Created {js_path}")

for root, dirs, files in os.walk(workspace):
    if any(ignore in root for ignore in ['.agents', '.backup', '.git']):
        continue
    
    for file in files:
        if file.endswith('.html'):
            html_path = os.path.join(root, file)
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.search(r'<link rel="stylesheet" href="(.*?)style\.css">', content)
            if match:
                prefix = match.group(1)
                script_tag = f'<script src="{prefix}copy_code.js"></script>'
                
                if script_tag not in content:
                    new_content = content.replace('</body>', f'  {script_tag}\\n</body>')
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Injected script into {html_path}")
