from wtforms.validators import *
from wtforms import *
from flask_wtf import FlaskForm

password_policy = [
    InputRequired(),
    Length(min=8, max=30, message='Password must be between 8 and 30 characters long.'),
    Regexp('.*[a-z]', message='Password must contain at least one lowercase letter.'),
    Regexp('.*[A-Z]', message='Password must contain at least one uppercase letter.'),
    Regexp(r'.*\d', message='Password must contain at least one number.')
]


class RegForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email address.'), Length(max=30)])
    name = StringField('name', validators=[InputRequired(), Length(max=30)])
    password = PasswordField('password', validators=password_policy)
    confirm = PasswordField('confirm', validators=[EqualTo('password', message='Passwords must match.')])


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email address.'), Length(max=30)])
    password = PasswordField('password')


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('new_password', validators=password_policy)
    confirm = PasswordField('confirm', validators=[EqualTo('new_password', message='Passwords must match.')])


class ResetPasswordForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email address.'), Length(max=30)])


class LabForm(FlaskForm):
    title = StringField('title')
