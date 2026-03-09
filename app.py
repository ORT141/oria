from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
import os
import json
import datetime
import random
from dotenv import load_dotenv
from openai import OpenAI
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv('config.env')

app = Flask(__name__)
app.secret_key = 'oria_very_secret_key' # In production, use a secure random key

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from models import db, User
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# Import and register blueprints
from routes.auth import auth_bp
from routes.views import views_bp
from routes.api import api_bp

app.register_blueprint(auth_bp)
app.register_blueprint(views_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
