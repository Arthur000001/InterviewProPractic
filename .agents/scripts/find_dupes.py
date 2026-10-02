import os
import re
import itertools
from collections import defaultdict

docs_dir = "/home/interviewer/Projects/InterviewPro/docs/questions/golang"

questions = []
for i in range(1, 14):
    for f in os.listdir(docs_dir):
        if f.startswith(f"topic_{i:02d}_") and f.endswith(".md"):
            filepath = os.path.join(docs_dir, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line_idx, line in enumerate(lines):
                    match = re.match(r'^\*\s*\[\s*\]\s*(.+)', line)
                    if match:
                        q_text = match.group(1).strip()
                        questions.append({
                            'text': q_text,
                            'file': filepath,
                            'line_idx': line_idx,
                            'topic': i
                        })
            break

def get_words(text):
    # simple tokenizer and stopword removal
    stopwords = {'что', 'такое', 'как', 'в', 'go', 'golang', 'и', 'для', 'с', 'по', 'а', 'на', 'от', 'чем', 'это', 'какие'}
    words = re.findall(r'\b\w+\b', text.lower())
    return set(w for w in words if w not in stopwords)

duplicates = []
seen_pairs = set()

for q1, q2 in itertools.combinations(questions, 2):
    w1 = get_words(q1['text'])
    w2 = get_words(q2['text'])
    
    if not w1 or not w2:
        continue
        
    intersection = len(w1.intersection(w2))
    union = len(w1.union(w2))
    jaccard = intersection / union if union > 0 else 0
    
    if jaccard > 0.75:
        # High similarity
        duplicates.append((jaccard, q1, q2))

duplicates.sort(key=lambda x: x[0], reverse=True)

with open('dupes_report.txt', 'w', encoding='utf-8') as f:
    for sim, q1, q2 in duplicates:
        f.write(f"SIM: {sim:.2f}\n")
        f.write(f"1 [{q1['topic']}]: {q1['text']}\n")
        f.write(f"2 [{q2['topic']}]: {q2['text']}\n")
        f.write("-" * 40 + "\n")

print(f"Found {len(duplicates)} potential duplicates.")
