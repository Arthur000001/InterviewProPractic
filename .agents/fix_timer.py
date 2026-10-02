import glob, re

for filepath in glob.glob("view/tasks/task_*.html"):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    # If timer-display has data-minutes="0", set it to "5"
    html = re.sub(r'data-minutes="0"', 'data-minutes="5"', html)
    html = re.sub(r'>00:00<', '>05:00<', html)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
