"""
Admin Panel Blueprint — ORIA RBAC.
Full title management + user attribute editing + search/sort + audit logging.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from models import db, User, ExclusiveTitle, AdminLog
from routes.decorators import admin_required, superadmin_required
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ── Audit Helper ─────────────────────────────────────────────────────────────
def log_action(action, target_user=None, old_value=None, new_value=None, details=None):
    """Record an admin action in the audit log."""
    entry = AdminLog(
        admin_id=g.user.id,
        admin_name=g.user.username,
        action=action,
        target_id=target_user.id if target_user else None,
        target_name=target_user.username if target_user else None,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        details=details,
    )
    db.session.add(entry)


# ── Dashboard ────────────────────────────────────────────────────────────────
@admin_bp.route('/')
@admin_required
def dashboard():
    """Main admin panel — list users, manage titles."""
    search_q = request.args.get('q', '').strip()
    sort_by = request.args.get('sort', 'id')
    sort_dir = request.args.get('dir', 'asc')
    role_filter = request.args.get('role', '')

    query = User.query

    if search_q:
        if search_q.isdigit():
            query = query.filter(User.id == int(search_q))
        else:
            query = query.filter(
                db.or_(
                    User.username.ilike(f'%{search_q}%'),
                    User.email.ilike(f'%{search_q}%'),
                )
            )

    if role_filter in ('user', 'admin', 'superadmin'):
        query = query.filter(User.role == role_filter)

    sort_columns = {
        'id': User.id, 'username': User.username,
        'level': User.level, 'coins': User.coins,
        'xp': User.xp, 'role': User.role,
    }
    sort_col = sort_columns.get(sort_by, User.id)
    query = query.order_by(sort_col.desc() if sort_dir == 'desc' else sort_col.asc())

    users = query.all()
    titles = ExclusiveTitle.query.order_by(ExclusiveTitle.id.asc()).all()

    all_users = User.query.all()
    stats = {
        'total_users': len(all_users),
        'total_admins': sum(1 for u in all_users if u.role in ('admin', 'superadmin')),
        'total_titled': sum(1 for u in all_users if u.equipped_title),
        'total_tg_linked': sum(1 for u in all_users if u.telegram_id),
        'avg_level': round(sum(u.level for u in all_users) / max(len(all_users), 1), 1),
        'total_coins': sum(u.coins for u in all_users),
    }

    return render_template(
        'admin/dashboard.html',
        users=users, titles=titles, stats=stats,
        current_user=g.user,
        search_q=search_q, sort_by=sort_by,
        sort_dir=sort_dir, role_filter=role_filter,
        active_tab='users',
    )


# ── Admin Logs Tab ───────────────────────────────────────────────────────────
@admin_bp.route('/logs')
@admin_required
def logs():
    """View audit logs with optional filtering."""
    action_filter = request.args.get('action', '')
    page = request.args.get('page', 1, type=int)
    per_page = 50

    query = AdminLog.query

    if action_filter:
        query = query.filter(AdminLog.action == action_filter)

    query = query.order_by(AdminLog.created_at.desc())
    total = query.count()
    logs_list = query.offset((page - 1) * per_page).limit(per_page).all()

    # Get distinct action types for filter dropdown
    action_types = db.session.query(AdminLog.action).distinct().order_by(AdminLog.action).all()
    action_types = [a[0] for a in action_types]

    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'admin/logs.html',
        logs=logs_list,
        action_types=action_types,
        action_filter=action_filter,
        page=page, total_pages=total_pages,
        current_user=g.user,
        active_tab='logs',
    )


# ── Title Management ─────────────────────────────────────────────────────────

@admin_bp.route('/title/create', methods=['POST'])
@admin_required
def create_title():
    name = request.form.get('title_name', '').strip()
    if not name:
        flash("Title name cannot be empty.", "error")
        return redirect(url_for('admin.dashboard'))
    if len(name) > 64:
        flash("Title too long (max 64 characters).", "error")
        return redirect(url_for('admin.dashboard'))
    if ExclusiveTitle.query.filter_by(name=name).first():
        flash(f"Title '{name}' already exists.", "error")
        return redirect(url_for('admin.dashboard'))

    db.session.add(ExclusiveTitle(name=name, is_system=False))
    log_action('create_title', details=f'Created title: {name}')
    db.session.commit()
    flash(f"Title '{name}' created.", "success")
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/title/delete/<int:title_id>', methods=['POST'])
@admin_required
def delete_title(title_id):
    title = db.session.get(ExclusiveTitle, title_id)
    if not title:
        flash("Title not found.", "error")
        return redirect(url_for('admin.dashboard'))
    if title.is_system:
        flash("Cannot delete a system title.", "error")
        return redirect(url_for('admin.dashboard'))

    affected = User.query.filter_by(equipped_title=title.name).all()
    for u in affected:
        u.equipped_title = ''

    log_action('delete_title', details=f'Deleted title: {title.name}, cleared from {len(affected)} user(s)')
    db.session.delete(title)
    db.session.commit()
    flash(f"Title '{title.name}' deleted.", "success")
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/title/force/<int:user_id>', methods=['POST'])
@admin_required
def force_title(user_id):
    target = db.session.get(User, user_id)
    if not target:
        flash("User not found.", "error")
        return redirect(url_for('admin.dashboard'))

    title_name = request.form.get('title_name', '').strip()
    if not title_name or len(title_name) > 64:
        flash("Invalid title.", "error")
        return redirect(url_for('admin.dashboard'))

    old = target.equipped_title
    target.equipped_title = title_name
    log_action('force_title', target, old_value=old, new_value=title_name)
    db.session.commit()
    flash(f"Title '{title_name}' → {target.username}.", "success")
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/title/remove/<int:user_id>', methods=['POST'])
@admin_required
def remove_title(user_id):
    target = db.session.get(User, user_id)
    if not target:
        flash("User not found.", "error")
        return redirect(url_for('admin.dashboard'))

    old = target.equipped_title
    target.equipped_title = ''
    log_action('remove_title', target, old_value=old, new_value='')
    db.session.commit()
    flash(f"Title removed from {target.username}.", "success")
    return redirect(url_for('admin.dashboard'))


# ── User Attribute Management ────────────────────────────────────────────────

@admin_bp.route('/user/modify/<int:user_id>', methods=['POST'])
@admin_required
def modify_user(user_id):
    target = db.session.get(User, user_id)
    if not target:
        flash("User not found.", "error")
        return redirect(url_for('admin.dashboard'))

    field = request.form.get('field', '').strip()
    try:
        delta = int(request.form.get('delta', 0))
    except (ValueError, TypeError):
        flash("Invalid value.", "error")
        return redirect(url_for('admin.dashboard'))

    if delta == 0:
        flash("No change (delta is 0).", "info")
        return redirect(url_for('admin.dashboard'))

    field_map = {
        'level': ('level', 1),      # (attr_name, min_value)
        'xp': ('xp', 0),
        'coins': ('coins', 0),
        'streak': ('current_streak', 0),
    }

    if field not in field_map:
        flash("Unknown field.", "error")
        return redirect(url_for('admin.dashboard'))

    attr, min_val = field_map[field]
    old = getattr(target, attr)
    new = max(min_val, old + delta)
    setattr(target, attr, new)
    log_action(f'modify_{field}', target, old_value=old, new_value=new)
    db.session.commit()
    flash(f"{target.username}: {field} {old} → {new}", "success")
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/user/reset-quests/<int:user_id>', methods=['POST'])
@admin_required
def reset_quests(user_id):
    target = db.session.get(User, user_id)
    if not target:
        flash("User not found.", "error")
        return redirect(url_for('admin.dashboard'))

    quest_count = len(target.get_quests())
    daily_count = len(target.get_daily_quests())
    target.quests = '[]'
    target.daily_quests = '[]'
    target.last_daily_date = ''
    log_action('reset_quests', target, details=f'Cleared {quest_count} quests + {daily_count} daily')
    db.session.commit()
    flash(f"Quests reset for {target.username}.", "success")
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/user/reset-chat/<int:user_id>', methods=['POST'])
@admin_required
def reset_chat(user_id):
    target = db.session.get(User, user_id)
    if not target:
        flash("User not found.", "error")
        return redirect(url_for('admin.dashboard'))

    msg_count = len(target.get_chat_history())
    target.chat_history = '[]'
    log_action('reset_chat', target, details=f'Cleared {msg_count} messages')
    db.session.commit()
    flash(f"Chat history cleared for {target.username}.", "success")
    return redirect(url_for('admin.dashboard'))


# ── Role Management (superadmin ONLY) ────────────────────────────────────────
@admin_bp.route('/role/update/<int:user_id>', methods=['POST'])
@superadmin_required
def update_role(user_id):
    target = db.session.get(User, user_id)
    if not target:
        flash("User not found.", "error")
        return redirect(url_for('admin.dashboard'))
    if target.is_superadmin:
        flash("Cannot modify a Super Admin's role.", "error")
        return redirect(url_for('admin.dashboard'))

    new_role = request.form.get('role', '').strip().lower()
    if new_role not in ('user', 'admin'):
        flash("Invalid role.", "error")
        return redirect(url_for('admin.dashboard'))

    old_role = target.role
    target.role = new_role
    log_action('update_role', target, old_value=old_role, new_value=new_role)
    db.session.commit()
    flash(f"Role for {target.username} → '{new_role}'.", "success")
    return redirect(url_for('admin.dashboard'))
