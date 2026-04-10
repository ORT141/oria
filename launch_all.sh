#!/bin/bash

# Configuration
ORIA_PATH="/Users/ancerian/oria"
BOT_PATH="/Users/ancerian/ORIA_Bot"

# Kill old instances if any
echo "🔍 Cleaning up previous processes..."
pkill -f "gunicorn.*app:app" 2>/dev/null
pkill -f "app.py" 2>/dev/null
pkill -f "bot.py" 2>/dev/null

# Function to run ORIA Web App (production: Gunicorn)
run_web() {
    echo "🌐 Starting ORIA Web App (Gunicorn)..."
    cd "$ORIA_PATH" || exit
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    # C-04: Use Gunicorn instead of python app.py
    gunicorn --bind 0.0.0.0:5001 \
             --workers 4 \
             --timeout 120 \
             --access-logfile "$ORIA_PATH/oria_access.log" \
             --error-logfile "$ORIA_PATH/oria_error.log" \
             app:app > oria_app.log 2>&1 &
}

# Function to run Telegram Bot
run_bot() {
    echo "🤖 Starting ORIA Telegram Bot..."
    cd "$BOT_PATH" || exit
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    python3 bot.py > oria_bot.log 2>&1 &
}

# Run them
run_web
sleep 2 # Small delay for web to initialize
run_bot

echo "✨ Both ORIA and the Telegram Bot are now running in the background."
echo "📜 Logs can be found in:"
echo "   - $ORIA_PATH/oria_app.log"
echo "   - $ORIA_PATH/oria_access.log"
echo "   - $ORIA_PATH/oria_error.log"
echo "   - $BOT_PATH/oria_bot.log"
echo "✅ Done!"
