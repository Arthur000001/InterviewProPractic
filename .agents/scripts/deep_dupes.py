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
                            'topic': i,
                            'filename': f
                        })
            break

def get_ngrams(text, n=3):
    text = re.sub(r'[^\w\s]', '', text.lower())
    # remove short common words
    words = [w for w in text.split() if w not in {'в', 'и', 'с', 'на', 'что', 'как', 'go', 'golang', 'это', 'для', 'по'}]
    text = "".join(words)
    if len(text) < n:
        return {text}
    return set(text[i:i+n] for i in range(len(text)-n+1))

candidates = []

for q1, q2 in itertools.combinations(questions, 2):
    w1 = get_ngrams(q1['text'])
    w2 = get_ngrams(q2['text'])
    
    if not w1 or not w2:
        continue
        
    intersection = len(w1.intersection(w2))
    union = len(w1.union(w2))
    jaccard = intersection / union if union > 0 else 0
    
    if jaccard > 0.4:  # Lower threshold with 3-grams
        candidates.append((jaccard, q1, q2))

candidates.sort(key=lambda x: x[0], reverse=True)

with open('deep_dupes_report.txt', 'w', encoding='utf-8') as f:
    for sim, q1, q2 in candidates:
        if q1['text'] != q2['text']:
            f.write(f"SIM: {sim:.2f}\n")
            f.write(f"1 [{q1['filename']}]: {q1['text']}\n")
            f.write(f"2 [{q2['filename']}]: {q2['text']}\n")
            f.write("-" * 50 + "\n")

print(f"Found {len([c for c in candidates if c[1]['text'] != c[2]['text']])} candidate pairs.")
