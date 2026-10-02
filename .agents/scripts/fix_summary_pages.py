import os
import shutil
import re

notes_dir = "/media/artur/BEA6-BBCE/InterviewPro/.notes"

# 1. Create topic_summary.html for Ozon and Flant
ozon_index = os.path.join(notes_dir, "companies/ozon/index.html")
ozon_summary = os.path.join(notes_dir, "companies/ozon/topic_summary.html")
shutil.copy2(ozon_index, ozon_summary)

flant_index = os.path.join(notes_dir, "companies/flant/index.html")
flant_summary = os.path.join(notes_dir, "companies/flant/topic_summary.html")
shutil.copy2(flant_index, flant_summary)

print("Created topic_summary.html for ozon and flant.")

# 2. Update all html files inside .notes ONLY
for root, dirs, files in os.walk(notes_dir):
    for f in files:
        if not f.endswith(".html"):
            continue
        p = os.path.join(root, f)
        with open(p, "r", encoding="utf-8") as fh:
            content = fh.read()

        new_content = content

        if p == os.path.join(notes_dir, "index.html"):
            # Update root index.html
            new_content = new_content.replace(
                'href="companies/ozon/index.html"',
                'href="companies/ozon/topic_summary.html"'
            )
            new_content = new_content.replace(
                'href="companies/flant/index.html"',
                'href="companies/flant/topic_summary.html"'
            )
        elif "/companies/ozon/" in p:
            # Inside ozon folder
            new_content = re.sub(
                r'href="index\.html"([^>]*)>📋 Итоги',
                r'href="topic_summary.html"\1>📋 Итоги',
                new_content
            )
            new_content = new_content.replace(
                'href="../flant/index.html"',
                'href="../flant/topic_summary.html"'
            )
        elif "/companies/flant/" in p:
            # Inside flant folder
            new_content = re.sub(
                r'href="index\.html"([^>]*)>📋 Итоги',
                r'href="topic_summary.html"\1>📋 Итоги',
                new_content
            )
            new_content = new_content.replace(
                'href="../ozon/index.html"',
                'href="../ozon/topic_summary.html"'
            )

        if new_content != content:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(new_content)
            print(f"Updated links in: {p}")

print("All summary links successfully updated!")
