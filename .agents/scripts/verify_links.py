import os
import re

docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs'))

def get_all_html_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.html'):
                file_list.append(os.path.join(root, f))
    return file_list

html_files = get_all_html_files(docs_dir)
print(f"Verifying links in {len(html_files)} HTML files...")

broken_links_count = 0
href_regex = re.compile(r'href="([^"#:]+)(?:#[^"]*)?"')

for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    dir_of_file = os.path.dirname(f)
    matches = href_regex.findall(content)
    
    for target in matches:
        if target.startswith('http') or target.startswith('mailto'):
            continue
        
        resolved_path = os.path.normpath(os.path.join(dir_of_file, target))
        if not os.path.exists(resolved_path):
            rel_path = os.path.relpath(f, docs_dir)
            print(f'[BROKEN LINK] in {rel_path}: href="{target}" -> {resolved_path} NOT FOUND')
            broken_links_count += 1

if broken_links_count == 0:
    print(f"ALL LINKS VERIFIED! 0 broken links found across all {len(html_files)} pages.")
else:
    print(f"Total broken links found: {broken_links_count}")
