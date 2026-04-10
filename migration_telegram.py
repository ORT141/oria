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
        
        # Helper to add column if not exists
        def add_column(table, column, type_def):
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}")
                print(f"Added '{column}' column to '{table}' successfully.")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"'{column}' column already exists.")
                else:
                    print(f"Error adding '{column}': {e}")

        # Add columns to 'user' table
        add_column("user", "telegram_id", "VARCHAR(64)")
        add_column("user", "role", "VARCHAR(20) DEFAULT 'user'")
        add_column("user", "created_at", "DATETIME") # Avoided DEFAULT CURRENT_TIMESTAMP due to SQLite ALTER limitation
        add_column("user", "prefix", "VARCHAR(100)")

        # Create unique index for telegram_id if it doesn't exist
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user_telegram_id ON user (telegram_id)")
            print("Ensured unique index on 'telegram_id'.")
        except Exception as e:
            print(f"Error creating index: {e}")
        
        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    upgrade_db()
