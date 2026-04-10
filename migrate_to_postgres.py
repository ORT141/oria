#!/usr/bin/env python3
"""
ORIA — SQLite → PostgreSQL Migration Script.

Usage:
    python migrate_to_postgres.py sqlite:///instance/users.db postgresql://user:pass@host:5432/oria

This script:
1. Reads all data from the SQLite database
2. Creates tables in PostgreSQL via SQLAlchemy
3. Copies all rows from every table
4. Preserves IDs and relationships
"""
import sys
import os

# Add parent directory to path so we can import models
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.orm import sessionmaker


def migrate(sqlite_url: str, pg_url: str):
    print(f"Source:  {sqlite_url}")
    print(f"Target:  {pg_url}")
    print()

    # Connect to both databases
    src_engine = create_engine(sqlite_url)
    dst_engine = create_engine(pg_url)

    # Reflect SQLite schema
    src_meta = MetaData()
    src_meta.reflect(bind=src_engine)

    # Create all tables in PostgreSQL using our models (ensures correct types)
    from models import db
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = pg_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        print("✅ PostgreSQL tables created")

    # Copy data table by table
    SrcSession = sessionmaker(bind=src_engine)
    DstSession = sessionmaker(bind=dst_engine)

    src_session = SrcSession()
    dst_session = DstSession()

    # Order matters for foreign keys (currently none, but future-proof)
    table_order = ['user', 'telegram_user', 'exclusive_title', 'admin_log']

    for table_name in table_order:
        if table_name not in src_meta.tables:
            print(f"⏭  Table '{table_name}' not in source DB — skipping")
            continue

        table = src_meta.tables[table_name]
        rows = src_session.execute(table.select()).fetchall()
        column_names = [c.name for c in table.columns]

        if not rows:
            print(f"⏭  Table '{table_name}' is empty — skipping")
            continue

        # Clear target table first
        dst_session.execute(text(f'DELETE FROM {table_name}'))

        # Insert rows
        for row in rows:
            row_dict = dict(zip(column_names, row))
            dst_session.execute(table.insert().values(**row_dict))

        dst_session.commit()
        print(f"✅ Migrated {len(rows)} rows → {table_name}")

    # Reset PostgreSQL sequences to match max IDs
    dst_inspector = inspect(dst_engine)
    for table_name in table_order:
        if table_name not in src_meta.tables:
            continue

        # Check if table has 'id' column
        columns = [c['name'] for c in dst_inspector.get_columns(table_name)]
        if 'id' in columns:
            result = dst_session.execute(text(f'SELECT MAX(id) FROM {table_name}')).scalar()
            if result:
                seq_name = f'{table_name}_id_seq'
                try:
                    dst_session.execute(text(f"SELECT setval('{seq_name}', {result})"))
                    dst_session.commit()
                    print(f"🔄 Reset sequence {seq_name} → {result}")
                except Exception as e:
                    dst_session.rollback()
                    print(f"⚠️  Could not reset sequence {seq_name}: {e}")

    src_session.close()
    dst_session.close()
    print()
    print("🎉 Migration complete!")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python migrate_to_postgres.py <sqlite_url> <postgresql_url>")
        print("Example: python migrate_to_postgres.py sqlite:///instance/users.db postgresql://user:pass@localhost:5432/oria")
        sys.exit(1)

    migrate(sys.argv[1], sys.argv[2])
