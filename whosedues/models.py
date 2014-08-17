from whosedues import db, app
import hashlib
from datetime import datetime
from functools import reduce


def hash_password(username, password):
    h = (username + ':' + password + ':' + app.config['SECRET_KEY']).encode('utf-8')
    for i in range(20):
        h = hashlib.sha256(h).hexdigest().encode('utf-8')
    return str(h)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(160))
    admin = db.Column(db.Boolean)
    registered_on = db.Column(db.DateTime)
    receipts = db.relationship('Receipt', backref='user', lazy='dynamic')
    dues = db.relationship('ReceiptDue', backref='user', lazy='dynamic')

    def __init__(self, username, password, email, name, password_hashed=False):
        self.username = str(username)
        if password_hashed:
            self.password_hash = str(password)
        else:
            self.password_hash = hash_password(username, password)
        self.email = str(email)
        self.name = str(name)
        self.admin = False
        self.registered_on = datetime.utcnow()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def get_gravatar_src(self):
        return 'https://www.gravatar.com/avatar/' + str(
            hashlib.md5(self.email.lower().encode('utf-8')).hexdigest())

    def owed_to(self, user):
        my_dues_to_them = filter(lambda x: x.receipt.user == user,
                                 self.dues.filter_by(paid=False).all())
        sum_my_dues = reduce(lambda x, y: x+y.amount, my_dues_to_them, 0)
        return sum_my_dues

    def __repr__(self):
        return '<User %r>' % (self.username)


class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String)
    amount = db.Column(db.Float)
    paid = db.Column(db.Boolean)
    time = db.Column(db.DateTime)
    dues = db.relationship('ReceiptDue', backref='receipt', lazy='dynamic')

    def __init__(self, user, amount, name='Untitled receipt', paid=False):
        self.user = user
        self.amount = amount
        self.name = name
        self.paid = paid
        self.time = datetime.utcnow()


class ReceiptDue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipt.id'))
    amount = db.Column(db.Float)
    paid = db.Column(db.Boolean)

    def __init__(self, user, receipt, amount, paid=False):
        self.user = user
        self.receipt = receipt
        self.amount = amount
        self.paid = paid
