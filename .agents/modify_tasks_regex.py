import os, glob, re

for filepath in glob.glob("view/tasks/task_*.html"):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()
        
    # We messed up earlier by deleting 🎯 from everywhere first.
    # But now the files are already saved with empty badges!
    # I need to restore the files from git or regenerate them!
