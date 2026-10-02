import os
import re

docs_dir = "/home/interviewer/Projects/InterviewPro/docs/questions/golang"
js_file = "/home/interviewer/Projects/InterviewPro/.agents/scripts/build_html_site.js"

# Old to New mapping
mapping = {
    7: 11,
    8: 12,
    9: 13,
    10: 10,
    11: 8,
    12: 7,
    13: 9,
}

# 1. Rename files safely
print("Renaming files...")
for ext in ['.md', '.html']:
    # First, move to tmp
    for old, new in mapping.items():
        for f in os.listdir(docs_dir):
            if f.startswith(f"topic_{old:02d}_") and f.endswith(ext):
                old_path = os.path.join(docs_dir, f)
                tmp_path = os.path.join(docs_dir, f"TMP_{new:02d}_" + f.split('_', 2)[2])
                os.rename(old_path, tmp_path)
                break
    # Then move tmp to final
    for f in os.listdir(docs_dir):
        if f.startswith("TMP_") and f.endswith(ext):
            tmp_path = os.path.join(docs_dir, f)
            final_name = f.replace("TMP_", "topic_")
            final_path = os.path.join(docs_dir, final_name)
            os.rename(tmp_path, final_path)

# 2. Update internal headings in .md files
print("Updating internal headings...")
for i in range(1, 14):
    for f in os.listdir(docs_dir):
        if f.startswith(f"topic_{i:02d}_") and f.endswith(".md"):
            filepath = os.path.join(docs_dir, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Use regex to find and replace the topic number in the # heading
            # e.g., # 🐹 Тема 12. Память
            new_content = re.sub(r'# (\S+)? Тема \d+\.', rf'# \1 Тема {i}.', content)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(new_content)
            break

# 3. Update build_html_site.js questionsConfig
print("Updating build_html_site.js...")
with open(js_file, 'r', encoding='utf-8') as f:
    js_content = f.read()

# We need to replace the entire golang array topics: [...]
new_topics = """    topics: [
      { slug: 'topic_01_basics', name: 'Тема 1. Основы языка Go' },
      { slug: 'topic_02_control_structures', name: 'Тема 2. Управляющие конструкции' },
      { slug: 'topic_03_functions_defer', name: 'Тема 3. Функции, Defer & Panic' },
      { slug: 'topic_04_methods_interfaces', name: 'Тема 4. Методы и Интерфейсы' },
      { slug: 'topic_05_oop_design', name: 'Тема 5. ООП и проектирование' },
      { slug: 'topic_06_io_data', name: 'Тема 6. Ввод-вывод и данные' },
      { slug: 'topic_07_memory_runtime', name: 'Тема 7. Память, GMP и GC' },
      { slug: 'topic_08_concurrency', name: 'Тема 8. Конкурентность и каналы' },
      { slug: 'topic_09_testing', name: 'Тема 9. Тестирование' },
      { slug: 'topic_10_dev_tools', name: 'Тема 10. Инструменты (vet, race)' },
      { slug: 'topic_11_frameworks', name: 'Тема 11. Практика и фреймворки' },
      { slug: 'topic_12_caching', name: 'Тема 12. Кэширование' },
      { slug: 'topic_13_observability', name: 'Тема 13. Observability & Логи' },
      { slug: 'topic_14_summary', name: 'Итоги: Все вопросы' }
    ]"""

js_content = re.sub(r'topics:\s*\[[\s\S]*?\{ slug: \'topic_14_summary\', name: \'Итоги: Все вопросы\' \}\s*\]', new_topics, js_content)

with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Done.")
