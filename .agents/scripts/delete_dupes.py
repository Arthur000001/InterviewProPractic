import re

files_to_check = [
    "/home/interviewer/Projects/InterviewPro/docs/questions/golang/topic_03_functions_defer.md",
    "/home/interviewer/Projects/InterviewPro/docs/questions/golang/topic_06_io_data.md",
    "/home/interviewer/Projects/InterviewPro/docs/questions/golang/topic_07_memory_runtime.md",
    "/home/interviewer/Projects/InterviewPro/docs/questions/golang/topic_08_concurrency.md",
    "/home/interviewer/Projects/InterviewPro/docs/questions/golang/topic_13_observability.md"
]

strings_to_delete = [
    "Почему рекомендуется избегать naked return",
    "Как GOMAXPROCS влияет на производительность?",
    "Что такое GOMAXPROCS?",
    "Когда использовать panic, а когда логировать ошибку?",
    "Может ли включённое профилирование замедлить приложение?",
    "Что показывает профиль блокировок?",
    "Как подключить профилирование к работающему веб-сервису?",
    "Как перенаправить вывод в файл или буфер?",
    "Какие основные функции используются для форматированного и неформатированного вывода данных в консоль?",
    "Как правильно проверить и сравнить ошибку?"
]

total_deleted = 0

for filepath in files_to_check:
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        deleted_here = False
        for s in strings_to_delete:
            if s in line and line.startswith("* [ ]"):
                # Delete this line and the following details block until </details>
                deleted_here = True
                total_deleted += 1
                break
        
        if deleted_here:
            # skip until </details>
            while i < len(lines) and "</details>" not in lines[i]:
                i += 1
            i += 1 # skip the </details> line itself
            # also skip empty lines after details
            while i < len(lines) and lines[i].strip() == "":
                i += 1
            continue
            
        new_lines.append(line)
        i += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

print(f"Deleted {total_deleted} duplicates.")
