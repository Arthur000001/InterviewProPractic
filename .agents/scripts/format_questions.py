import os
import re

def format_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    counter = 1
    def replace_match(match):
        nonlocal counter
        res = f"{counter}. "
        counter += 1
        return res

    new_content = re.sub(r'\* \[ \] ', replace_match, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Formatted {file_path}")

files = [
    'docs/questions/golang/topic_01_basics.md',
    'docs/questions/golang/topic_04_methods_interfaces.md',
    'docs/questions/golang/topic_05_oop_design.md'
]

for file in files:
    format_file(file)
