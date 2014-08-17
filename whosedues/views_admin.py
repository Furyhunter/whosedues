from flask_login import current_user
from flask import redirect, url_for, flash, render_template, request
from whosedues.models import *
from functools import wraps
from whosedues import app, db


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated() and current_user.admin:
            return func(*args, **kwargs)
        else:
            flash('You are not an administrator.', 'error')
            return redirect(url_for('index'))
    return decorated_view


@app.route('/admin')
@admin_required
def admin_index():
    return render_template('admin/index.html', users=User.query.all())


@app.route('/admin/delete_user', methods=['POST'])
@admin_required
def admin_delete_user():
    u = User.query.filter_by(id=request.form['user_id']).first()
    if u is None:
        flash('User does not exist')
        return redirect(url_for('admin'))

    if u == current_user:
        flash('You cannot delete your own user.')
        return redirect(url_for('admin'))

    for d in u.dues:
        db.session.delete(d)
    for r in u.receipts:
        db.session.delete(r)
    db.session.delete(u)
    db.session.commit()
    flash('User \'%s\' has been deleted.' % u.username)
    return redirect(url_for('admin_index'))


@app.route('/admin/set_admin', methods=['POST'])
@admin_required
def admin_set_admin():
    u = User.query.filter_by(id=request.form['user_id']).first()
    if u is None:
        flash('User does not exist')
        return redirect(url_for('admin'))

    if u == current_user:
        flash('You cannot set your own admin status.')
        return redirect(url_for('admin'))

    if request.form['admin'] == 'True':
        u.admin = True
        flash('User \'%s\' is now an admin' % u.username)
    else:
        u.admin = False
        flash('User \'%s\' is no longer an admin' % u.username)

    db.session.add(u)
    db.session.commit()
    return redirect(url_for('admin_index'))
