from whosedues import db
import hashlib
from datetime import datetime


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).digest()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    registered_on = db.Column(db.DateTime)
    receipts = db.relationship('Receipt', backref='user', lazy='dynamic')

    def __init__(self, username, password, email, password_hashed=False):
        self.username = username
        if password_hashed:
            self.password_hash = password
        else:
            self.password_hash = hash_password(password)
        self.email = email
        self.registered_on = datetime.utcnow()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

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
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipt.id'))
    amount = db.Column(db.Float)
    paid = db.Column(db.Boolean)

    def __init__(self, user, receipt, amount, paid=False):
        self.user = user
        self.receipt = receipt
        self.amount = amount
        self.paid = paid
