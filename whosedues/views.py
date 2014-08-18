from whosedues import app, login_manager, db
from whosedues.models import *
from flask_login import login_required, login_user, logout_user, current_user
from flask import render_template, request, flash, redirect, url_for, abort
from sqlalchemy import desc
from whosedues.forms import *


@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@app.route('/')
@login_required
def index():
    balances = [(user, current_user.owed_to(user) - user.owed_to(current_user))
                for user in
                User.query.filter(User.id != current_user.id).all()]
    balances = list(filter(lambda x: x[1] != 0, balances))
    total_balance = reduce(lambda a, i: a + i[1], balances, 0)
    return render_template('index.html', balances=balances,
                           total_balance=total_balance)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data,
                                 password_hash=
                                 hash_password(form.username.data,
                                               form.password.data)).first()
        if u is not None:
            login_user(u)
            flash('Logged in successfully.', 'info')
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/user/all')
@login_required
def all_users():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_active():
        flash('You cannot register for an account while logged in.', 'error')
        return redirect(url_for('index'))

    if app.config['REGISTRATIONS_OPEN'] is False:
        flash('Registrations are closed.', 'error')
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        u = User(form.username.data,
                 form.password.data,
                 form.email.data,
                 form.name.data)
        db.session.add(u)
        db.session.commit()
        if len(User.query.all()) == 1:
            u.admin = True
            db.session.add(u)
            db.session.commit()
            flash('As first user, you are automatically set as admin.', 'info')
        flash('Registered successfully', 'info')
        login_user(u)
        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/user/<int:userid>')
@login_required
def view_user(userid):
    u = User.query.filter_by(id=userid).first_or_404()
    receipts = u.receipts.order_by(desc('time')).all()

    return render_template('view_user.html', user=u, receipts=receipts)


@app.route('/user/change_password', methods=['GET', 'POST'])
@login_required
def user_change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        hash_current = hash_password(current_user.username, form.current.data)
        if hash_current != current_user.password_hash:
            flash('Current password was invalid', 'error')
            return redirect(url_for('user_change_password'))
        current_user.password_hash = hash_password(
            current_user.username, form.newpass.data)
        db.session.add(current_user)
        db.session.commit()
        flash('Password changed successfully.', 'info')
        return redirect(url_for('index'))
    return render_template('change_password.html', form=form)


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
@login_required
def all_receipts():
    receipts = Receipt.query.order_by(desc('time')).all()
    return render_template('all_receipts.html', receipts=receipts)


@app.route('/receipt/<int:receipt_id>')
@login_required
def view_receipt(receipt_id):
    receipt = Receipt.query.filter_by(id=receipt_id).first_or_404()
    due_form = AddDueForm()
    valid_users = [(u.id, u.name) for u in User.query.order_by('name')]
    for u in valid_users:
        if u[0] == current_user.id:
            valid_users.remove(u)
    due_form.user.choices = valid_users
    dues = receipt.dues.all()

    if receipt is None:
        abort(404)
    return render_template('view_receipt.html', receipt=receipt,
                           due_form=due_form, dues=dues)


@app.route('/receipt/<int:receipt_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_receipt(receipt_id):
    receipt = Receipt.query.filter_by(id=receipt_id).first_or_404()
    if receipt is None:
        abort(404)
    if request.method == 'GET':
        return render_template('confirm_delete_receipt.html', receipt=receipt)

    for d in dues:
        db.session.delete(d)
    db.session.delete(receipt)
    db.session.commit()
    return redirect(
        request.args.get('next') or url_for('view_user',
                                            userid=current_user.id))


@app.route('/receipt/<int:receipt_id>/due/add', methods=['POST'])
@login_required
def due_add(receipt_id):
    receipt = Receipt.query.filter_by(id=receipt_id).first_or_404()

    form = AddDueForm()
    form.user.choices = [(u.id, u.name) for u in User.query.order_by('name')]
    if form.validate_on_submit():
        u = User.query.filter_by(id=form.user.data).first_or_404()
        previous_due = u.dues.filter_by(receipt_id=receipt.id).first()

        if form.amount.data == 0 and previous_due is not None:
            db.session.delete(previous_due)
            db.session.commit()
            flash('Due removed successfully')
        elif form.amount.data == 0 and previous_due is None:
            flash('Nothing to do.')
        elif previous_due is None:
            due = ReceiptDue(u, receipt, form.amount.data)
            db.session.add(due)
            db.session.commit()
            flash('Due created successfully')
        else:
            previous_due.amount = form.amount.data
            db.session.add(previous_due)
            db.session.commit()
            flash('Due updated successfully')
    else:
        flash('Form not filled out')

    return redirect(
        request.args.get(
            'next', url_for('view_receipt', receipt_id=receipt_id)))


@app.route('/pay_dues_between/<int:user_id>', methods=['GET', 'POST'])
def pay_dues_between(user_id):
    u = User.query.filter_by(id=user_id).first_or_404()

    balance = current_user.owed_to(u) - u.owed_to(current_user)
    if balance <= 0:
        flash('You do not need to pay that user at this time.')
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('pay_dues_between.html', user=u, balance=balance)

    their_unpaid_dues = list(filter(lambda b: b.receipt.user == current_user,
                               u.dues.filter_by(paid=False)))
    my_unpaid_dues = list(filter(lambda b: b.receipt.user == u,
                            current_user.dues.filter_by(paid=False)))
    for d in their_unpaid_dues + my_unpaid_dues:
        d.paid = True
        db.session.add(d)
    db.session.commit()

    flash('All dues between the targets have been marked as paid.', 'info')
    return redirect(url_for('index'))


@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('You must be logged in.')
    return redirect(url_for('login'))


@app.template_filter('currency')
def format_currency(value):
    return '${:,.2f}'.format(value)


@app.template_filter('timesince')
def friendly_time(dt, past_="ago",
                  future_="from now",
                  default="just now"):
    """
    Returns string representing "time since"
    or "time until" e.g.
    3 days ago, 5 hours from now etc.
    """

    now = datetime.utcnow()
    if now > dt:
        diff = now - dt
        dt_is_past = True
    else:
        diff = dt - now
        dt_is_past = False

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:

        if period:
            return "%d %s %s" % (period,
                                 singular if period == 1 else plural,
                                 past_ if dt_is_past else future_)

    return default


if __name__ == '__main__':
    app.run()
    login_manager.init_app(app)
