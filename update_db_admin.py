"""
Migration: Add 'role' and 'prefix' columns to the User table.
Run once: python update_db_admin.py
"""
from app import app, db
from sqlalchemy import text, inspect

def migrate():
    with app.app_context():
        inspector = inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('user')]

        with db.engine.connect() as conn:
            if 'role' not in existing_columns:
                conn.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL"))
                conn.commit()
                print("✅ Added 'role' column to User table.")
            else:
                print("ℹ️  'role' column already exists, skipping.")

            if 'prefix' not in existing_columns:
                conn.execute(text("ALTER TABLE user ADD COLUMN prefix VARCHAR(100)"))
                conn.commit()
                print("✅ Added 'prefix' column to User table.")
            else:
                print("ℹ️  'prefix' column already exists, skipping.")

        print("\n🎉 Migration complete!")

if __name__ == '__main__':
    migrate()
