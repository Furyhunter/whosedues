from whosedues import app, login_manager, db
from whosedues.models import *
from flask_login import login_required, login_user, logout_user, current_user
from flask import render_template, request, flash, redirect, url_for, abort
from whosedues.forms import *


@app.route('/')
def index():
    return render_template('index.html')


@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data,
                                 password_hash=
                                 hash_password(form.password.data)).first()
        if u is not None:
            login_user(u)
            flash('Logged in successfully.', 'info')
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/user/all')
def all_users():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_active():
        flash('You cannot register for an account while logged in.', 'error')
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        u = User(form.username.data,
                 form.password.data,
                 form.email.data)
        db.session.add(u)
        db.session.commit()
        flash('Registered successfully', 'info')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/user/<int:userid>')
def view_user(userid):
    u = User.query.filter_by(id=userid).first()
    receipts = u.receipts.all()
    if u is None:
        abort(404)

    return render_template('view_user.html', user=u, receipts=receipts)


@app.route('/receipt/add', methods=['GET', 'POST'])
@login_required
def add_receipt():
    form = AddReceiptForm()
    if form.validate_on_submit():
        r = Receipt(current_user, form.amount.data, form.name.data)
        db.session.add(r)
        db.session.commit()
        return redirect(url_for('view_receipt', receipt_id=r.id))
    return render_template('add_receipt.html', form=form)


@app.route('/receipt/all')
def all_receipts():
    receipts = Receipt.query.all()
    return render_template('all_receipts.html', receipts=receipts)


@app.route('/receipt/<int:receipt_id>')
def view_receipt(receipt_id):
    receipt = Receipt.query.filter_by(id=receipt_id).first()
    if receipt is None:
        abort(404)
    return render_template('view_receipt.html', receipt=receipt)


@app.route('/receipt/<int:receipt_id>/delete', methods=['GET', 'POST'])
def delete_receipt(receipt_id):
    receipt = Receipt.query.filter_by(id=receipt_id).first()
    if receipt is None:
        abort(404)
    if request.method == 'GET':
        return render_template('confirm_delete_receipt.html', receipt=receipt)

    db.session.delete(receipt)
    db.session.commit()
    return redirect(
        request.args.get('next') or url_for('view_user',
                                            userid=current_user.id))


def format_currency(value):
    return '${:,.2f}'.format(value)


app.jinja_env.filters['currency'] = format_currency


if __name__ == '__main__':
    app.run()
    login_manager.init_app(app)
