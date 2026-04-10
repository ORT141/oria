from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import os
import json
import datetime
import logging
import random
from dotenv import load_dotenv
from openai import OpenAI
from werkzeug.security import generate_password_hash, check_password_hash

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("oria_app")

# Load environment variables
load_dotenv('config.env')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    raise RuntimeError("FATAL: SECRET_KEY environment variable is not set!")

# ── Session Cookie Hardening (W-05) ──────────────────────────────────────────
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# ── CSRF Protection (W-01) ──────────────────────────────────────────────────
csrf = CSRFProtect(app)

# ── Database Configuration ──────────────────────────────────────────────────
db_url = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
# Heroku-style fix: postgres:// → postgresql://
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB-specific engine options
if db_url.startswith('sqlite'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {"timeout": 30},
        "pool_pre_ping": True,
    }
else:
    # PostgreSQL pool settings
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
    }

from models import db, User, ExclusiveTitle, AdminLog
db.init_app(app)

# Create database tables + enable WAL mode for SQLite (C-06)
with app.app_context():
    db.create_all()
    if db_url.startswith('sqlite'):
        try:
            from sqlalchemy import text
            db.session.execute(text("PRAGMA journal_mode=WAL"))
            db.session.commit()
            logger.info("SQLite WAL mode enabled")
        except Exception as e:
            logger.warning("Could not enable SQLite WAL mode: %s", e)

    # ── Super Admin Auto-Promotion ────────────────────────────────────────
    super_admin_email = os.environ.get('SUPER_ADMIN_EMAIL')
    if super_admin_email:
        try:
            sa_user = User.query.filter_by(email=super_admin_email).first()
            if sa_user and sa_user.role != 'superadmin':
                sa_user.role = 'superadmin'
                db.session.commit()
                logger.info("Super admin role assigned to %s", sa_user.email)
            elif sa_user:
                logger.info("Super admin already confirmed: %s", sa_user.email)
            else:
                logger.warning("SUPER_ADMIN_EMAIL '%s' not found in DB (user may not have registered yet)", super_admin_email)
        except Exception as e:
            db.session.rollback()
            logger.warning("Super admin auto-promotion skipped (DB may need migration): %s", e)

    # ── Seed System Titles from LEVEL_REWARDS ─────────────────────────────
    try:
        from routes.api import LEVEL_REWARDS
        system_titles = [r['title'] for r in LEVEL_REWARDS.values() if r.get('title')]
        for title_name in system_titles:
            exists = ExclusiveTitle.query.filter_by(name=title_name).first()
            if not exists:
                db.session.add(ExclusiveTitle(name=title_name, is_system=True))
        db.session.commit()
        logger.info("System titles seeded: %s", system_titles)
    except Exception as e:
        db.session.rollback()
        logger.warning("Title seeding skipped: %s", e)

# Import and register blueprints
from routes.auth import auth_bp
from routes.views import views_bp
from routes.api import api_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(views_bp)
app.register_blueprint(api_bp)
app.register_blueprint(admin_bp)

# ── Exempt JSON API routes from CSRF (they use session-based auth, not forms) ──
csrf.exempt(api_bp)

if __name__ == '__main__':
    # C-04: debug=False for production safety
    app.run(debug=False, port=5001)
