from wtforms import *
from flask_wtf.html5 import *
from flask_wtf import Form


class LoginForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=40)])
    password = PasswordField('Password', [validators.Length(min=4, max=80)])


class RegisterForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=40)])
    email = EmailField('Email Address', [validators.Length(min=4, max=80)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match.'),
        validators.Length(min=4,max=80)])
    confirm = PasswordField('Repeat Password')
    name = TextField('Name', [validators.Length(min=4, max=160)])


class AddReceiptForm(Form):
    name = TextField('Receipt Name', [validators.Length(min=5, max=40)])
    amount = DecimalField('Total', [validators.NumberRange(min=0, max=None)])


class AddDueForm(Form):
    user = SelectField('User', coerce=int)
    amount = DecimalField('Amount', [validators.NumberRange(min=0, max=None)])


class ChangePasswordForm(Form):
    current = PasswordField('Current Password', [validators.Required()])
    newpass = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match.'),
        validators.Length(min=4,max=80)])
    confirm = PasswordField('Repeat Password')
