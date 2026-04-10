from flask import Blueprint, render_template, redirect, url_for, session
from models import db, User

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('views.home'))
    return render_template('landing.html')

@views_bp.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    from flask import request
    if 'user_id' not in session:
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        user = db.session.get(User, session['user_id'])
        if user:
            onboarding = {
                'q1': request.form.get('q1', '').strip(),
                'q2': request.form.get('q2', '').strip(),
                'q3': request.form.get('q3', '').strip(),
                'q4': request.form.get('q4', '').strip(),
                'q5': request.form.get('q5', '').strip(),
            }
            user.set_onboarding_data(onboarding)
            db.session.commit()
        return redirect(url_for('views.home'))


    return render_template('onboarding.html')

@views_bp.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.register'))
    
    user = db.session.get(User, session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.register'))

    return render_template('homes.html', user=user)

@views_bp.route('/link-telegram')
def link_telegram():
    from flask import request, flash
    tg_id = request.args.get('tg_id')
    
    if not tg_id:
        flash("Invalid Telegram link. Missing ID.", "error")
        return redirect(url_for('views.index'))

    # If user is logged in, link immediately
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        if user:
            existing_link = User.query.filter_by(telegram_id=tg_id).first()
            if existing_link and existing_link.id != user.id:
                flash("This Telegram account is already linked to another user.", "error")
            else:
                user.telegram_id = tg_id
                db.session.commit()
                flash("Telegram successfully linked!", "success")
        return redirect(url_for('views.home'))
    
    # Not logged in: store in session and redirect to login
    session['pending_tg_id'] = tg_id
    flash("Please log in to link your Telegram account.", "info")
    return redirect(url_for('auth.login'))
