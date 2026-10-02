import json
import html
import subprocess
import re

with open("/home/interviewer/Projects/InterviewProPractic/.agents/extracted_tasks.json", "r", encoding="utf-8") as f:
    extracted_tasks = json.load(f)

def format_go_code(code_str):
    if not code_str:
        return ""
    
    lines = code_str.split('\n')
    text_lines = []
    go_lines = []
    
    in_go = False
    for line in lines:
        if not in_go and re.match(r'^\s*(package|import|func|type|var|const)', line):
            in_go = True
        
        if in_go:
            go_lines.append(line)
        else:
            text_lines.append(line)
            
    if not go_lines:
        return code_str
        
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
            print("Gofmt failed:", res.stderr.decode('utf-8'))
            return code_str
    except Exception as e:
        return code_str

for i, t in enumerate(extracted_tasks):
    if t['code']:
        fmt = format_go_code(t['code'])
        if fmt == t['code']:
            print(f"Task {i} code was NOT formatted by gofmt.")
