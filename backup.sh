#!/bin/bash

# BrainRush Database Backup Script
# Використання: ./backup.sh [restore]

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="brainrush_app"
DB_PATH="/app/instance/brainrush.db"

# Створюємо директорію для бекапів якщо не існує
mkdir -p "$BACKUP_DIR"

# Функція для створення бекапу
backup() {
    echo "📦 Creating database backup..."
    
    # Перевіряємо чи контейнер запущений
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        echo "❌ Error: Container $CONTAINER_NAME is not running"
        exit 1
    fi
    
    # Створюємо бекап
    docker exec "$CONTAINER_NAME" cp "$DB_PATH" "/tmp/backup_${TIMESTAMP}.db"
    docker cp "${CONTAINER_NAME}:/tmp/backup_${TIMESTAMP}.db" "${BACKUP_DIR}/brainrush_backup_${TIMESTAMP}.db"
    docker exec "$CONTAINER_NAME" rm "/tmp/backup_${TIMESTAMP}.db"
    
    echo "✅ Backup created: ${BACKUP_DIR}/brainrush_backup_${TIMESTAMP}.db"
    
    # Видаляємо старі бекапи (зберігаємо останні 7)
    cd "$BACKUP_DIR"
    ls -t brainrush_backup_*.db | tail -n +8 | xargs -r rm
    echo "🧹 Old backups cleaned (keeping last 7)"
}

# Функція для відновлення з бекапу
restore() {
    if [ -z "$1" ]; then
        echo "❌ Error: Please specify backup file"
        echo "Usage: ./backup.sh restore <backup_file>"
        echo "Available backups:"
        ls -1 "$BACKUP_DIR"/brainrush_backup_*.db 2>/dev/null || echo "  No backups found"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        echo "❌ Error: Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    echo "⚠️  WARNING: This will overwrite the current database!"
    read -p "Continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "❌ Restore cancelled"
        exit 0
    fi
    
    echo "🔄 Restoring database from $BACKUP_FILE..."
    
    # Зупиняємо контейнер
    docker-compose stop web
    
    # Копіюємо бекап
    docker cp "$BACKUP_FILE" "${CONTAINER_NAME}:${DB_PATH}"
    
    # Запускаємо контейнер
    docker-compose start web
    
    echo "✅ Database restored successfully"
}

# Головна логіка
case "${1:-backup}" in
    backup)
        backup
        ;;
    restore)
        restore "$2"
        ;;
    *)
        echo "Usage: $0 {backup|restore <file>}"
        exit 1
        ;;
esac