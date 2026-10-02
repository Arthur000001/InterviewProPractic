import os
import re

golang_dir = "/home/interviewer/Projects/InterviewPro/docs/questions/golang"
output_file = os.path.join(golang_dir, "topic_14_summary.md")

questions = []
seen_normalized = set()

def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

for i in range(1, 14):
    filename = f"topic_{i:02d}"
    # find the actual file, as it might have suffixes
    # Actually they are exactly topic_01_basics.md, etc.
    # Let's list the files to get exact names
    for f in os.listdir(golang_dir):
        if f.startswith(f"topic_{i:02d}_") and f.endswith(".md"):
            filepath = os.path.join(golang_dir, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    match = re.match(r'^\*\s*\[\s*\]\s*(.+)', line)
                    if match:
                        q_text = match.group(1).strip()
                        norm = normalize(q_text)
                        if norm not in seen_normalized:
                            seen_normalized.add(norm)
                            questions.append(q_text)
            break

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# 🐹 Итоги: Все вопросы GoLang\n\n")
    f.write("<div style=\"display: flex; gap: 10px; margin-bottom: 20px;\">\n")
    f.write("  <button class=\"btn\" onclick=\"alert('Собеседование')\">Собеседование</button>\n")
    f.write("  <button class=\"btn\" onclick=\"alert('Квизы')\">Квизы</button>\n")
    f.write("</div>\n\n")
    f.write("Полный сводный список уникальных вопросов по Go:\n\n")
    for q in questions:
        f.write(f"* [ ] {q}\n")

print(f"Extracted {len(questions)} unique questions.")
