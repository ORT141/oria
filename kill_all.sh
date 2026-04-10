#!/bin/bash

# Скрипт для корректной остановки всех компонентов ORIA (Backend + Bot)

echo "🔍 Поиск и завершение активных процессов ORIA..."

# 1. Останавливаем Бэкенд (Gunicorn)
if pkill -f "gunicorn.*app:app" 2>/dev/null; then
    echo "✅ Gunicorn (Backend) успешно остановлен."
else
    echo "ℹ️ Gunicorn не был запущен."
fi

# 2. На всякий случай убиваем прямые запуски app.py (если запускали не через Gunicorn)
pkill -f "app.py" 2>/dev/null

# 3. Останавливаем Telegram Бота
if pkill -f "bot.py" 2>/dev/null; then
    echo "✅ ORIA Bot успешно остановлен."
else
    echo "ℹ️ Процесс бота не найден."
fi

echo "---------------------------------------"
echo "✨ Чистка завершена. Все компоненты ORIA выключены."
