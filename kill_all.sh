#!/bin/bash

# Скрипт для корректной остановки ORIA (Backend + embedded Bot)

echo "🔍 Поиск и завершение активных процессов ORIA..."

# 1. Останавливаем Бэкенд (Gunicorn) — бот умрёт вместе с ним (daemon thread)
if pkill -f "gunicorn.*app:app" 2>/dev/null; then
    echo "✅ Gunicorn (Backend + Bot) успешно остановлен."
else
    echo "ℹ️ Gunicorn не был запущен."
fi

# 2. На всякий случай убиваем прямые запуски app.py
pkill -f "python.*app.py" 2>/dev/null

echo "---------------------------------------"
echo "✨ Чистка завершена. Все компоненты ORIA выключены."
