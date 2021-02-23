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
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email address.'), Length(max=30)], render_kw={"placeholder": "Email"})
    password = PasswordField('password', render_kw={"placeholder": "Password"})


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('new_password', validators=password_policy)
    confirm = PasswordField('confirm', validators=[EqualTo('new_password', message='Passwords must match.')])


class ResetPasswordForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email address.'), Length(max=30)])


class LabForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(max=30)])
    tags = StringField('tags')
    title = StringField('title')


class CourseForm(FlaskForm):
    name = StringField('name', validators=[InputRequired()])


class SchoolForm(FlaskForm):
    name = StringField('name', validators=[InputRequired()])


class TagForm(FlaskForm):
    name = StringField('name', validators=[InputRequired()])


class JoinForm(FlaskForm):
    join_code = StringField('join_code', validators=[InputRequired(), Length(max=6)],
                            render_kw={"placeholder": "xxxxxx", 'maxlength': '6', 'minlength': '6'})
