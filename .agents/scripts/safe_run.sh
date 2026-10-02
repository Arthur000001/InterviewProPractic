#!/bin/bash
# Использование: .agents/scripts/safe_run.sh <команда>
# Пример: .agents/scripts/safe_run.sh python3 script.py

# Папка для бэкапов внутри .agents
BACKUP_DIR=".agents/tmp/backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.zip"

echo "📦 Создание резервной копии..."

DIRS_TO_BACKUP=""
if [ -d ".notes" ]; then
    DIRS_TO_BACKUP="$DIRS_TO_BACKUP .notes"
fi
if [ -d "docs" ]; then
    DIRS_TO_BACKUP="$DIRS_TO_BACKUP docs"
fi

if [ -n "$DIRS_TO_BACKUP" ]; then
    zip -r -q "$BACKUP_FILE" $DIRS_TO_BACKUP
    echo "✅ Бэкап сохранен в $BACKUP_FILE"
else
    echo "⚠️ Папки docs и .notes не найдены, бэкап не создан."
fi

echo "🚀 Запуск: $@"
echo "----------------------------------------"
"$@"
