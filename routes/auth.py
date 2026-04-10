from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('e-mail')
        password = request.form.get('password')
        pronouns_list = request.form.getlist('pronoun')
        pronouns = ", ".join(pronouns_list)

        # W-04: Password strength validation
        if not password or len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for('auth.register'))

        if not name or not email:
            flash("Username and email are required.", "error")
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter(
            (User.username == name) | (User.email == email)
        ).first()
        if existing_user:
            flash("Username or email is already in use. Please try a different one.", "error")
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=name, email=email, password=hashed_password, pronouns=pronouns)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session.permanent = True

        # Link Telegram if pending
        pending_tg_id = session.get('pending_tg_id')
        if pending_tg_id:
            existing_link = User.query.filter_by(telegram_id=pending_tg_id).first()
            if not existing_link:
                new_user.telegram_id = pending_tg_id
                db.session.commit()
                flash("Telegram successfully linked!", "success")
            session.pop('pending_tg_id', None)

        return redirect(url_for('views.onboarding'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('e-mail')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True

            # Link Telegram if pending
            pending_tg_id = session.get('pending_tg_id')
            if pending_tg_id:
                existing_link = User.query.filter_by(telegram_id=pending_tg_id).first()
                if not existing_link:
                    user.telegram_id = pending_tg_id
                    db.session.commit()
                    flash("Telegram successfully linked!", "success")
                else:
                    flash("Could not link Telegram: ID already in use by another account.", "error")
                session.pop('pending_tg_id', None)

            return redirect(url_for('views.home'))
        else:
            flash("Invalid email or password!", "error")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.register'))
