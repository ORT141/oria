#!/bin/bash

# Configuration
ORIA_PATH="/Users/ancerian/oria"

# Kill old instances if any
echo "🔍 Cleaning up previous processes..."
pkill -f "gunicorn.*app:app" 2>/dev/null
pkill -f "app.py" 2>/dev/null

# Function to run ORIA Web App + Bot (production: Gunicorn)
run_web() {
    echo "🌐 Starting ORIA (Web + Bot)..."
    cd "$ORIA_PATH" || exit
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    # C-04: Use Gunicorn instead of python app.py
    # --preload: load app once in master → bot thread starts only once
    gunicorn --bind 0.0.0.0:5001 \
             --workers 4 \
             --timeout 120 \
             --preload \
             --access-logfile "$ORIA_PATH/oria_access.log" \
             --error-logfile "$ORIA_PATH/oria_error.log" \
             app:app > oria_app.log 2>&1 &
}

# Run
run_web

echo "✨ ORIA (Web + Telegram Bot) is now running in the background."
echo "📜 Logs can be found in:"
echo "   - $ORIA_PATH/oria_app.log"
echo "   - $ORIA_PATH/oria_access.log"
echo "   - $ORIA_PATH/oria_error.log"
echo "✅ Done!"
