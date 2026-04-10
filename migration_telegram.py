import sqlite3
import os

def upgrade_db():
    # Detect database path
    db_path = 'instance/users.db'
    if not os.path.exists(db_path):
        # Fallback for relative path
        db_path = 'users.db'
        if not os.path.exists(db_path):
            print(f"Database not found at instance/users.db or users.db")
            return
    
    print(f"Using database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add telegram_id column without UNIQUE constraint (SQLite limitation)
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN telegram_id VARCHAR(64)")
            print("Added 'telegram_id' column successfully.")
            
            # Create a unique index for telegram_id
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user_telegram_id ON user (telegram_id)")
            print("Created unique index on 'telegram_id'.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("'telegram_id' column already exists.")
            else:
                print(f"Error adding 'telegram_id': {e}")
        
        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    upgrade_db()
