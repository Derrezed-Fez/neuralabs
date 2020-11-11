from neuralabs.forms import ResetPasswordForm, RegForm, LoginForm, ChangePasswordForm, LabForm
from neuralabs.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, request, redirect, url_for
from neuralabs.__init__ import app
import datetime
import base64
import bson
from bson.binary import Binary

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            existing_user = User.objects(email=form.email.data).first()
            if existing_user is None:
                hash_pass = generate_password_hash(form.password.data, method='pbkdf2:sha256:80000')
                new_user = User(form.name.data, form.email.data, hash_pass)
                new_user.join_date = datetime.datetime.now
                new_user.save()
                login_user(new_user)
                return redirect(url_for('dashboard'))
    return render_template('accounts/register.html', page='Register', form=form)


@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            check_user = User.objects(email=form.email.data).first()
            if check_user:
                if check_password_hash(check_user['password'], form.password.data):
                    login_user(check_user)
                    return redirect(url_for('dashboard'))
            form.errors['invalid'] = ['Invalid username or password.']
    return render_template('accounts/login.html', page='Login', form=form)


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if not current_user.is_authenticated:  # TODO: Add support for one time log in token after resetting password.
        return redirect(url_for('reset_password'))
    form = ChangePasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.is_authenticated:
                current_user.password = generate_password_hash(form.new_password.data, method='pbkdf2:sha256:80000')
                current_user.save()
    return render_template('accounts/change_password.html', page='Change Password', user=current_user, form=form)


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    return render_template('accounts/reset-password.html', page='Reset Password', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    user_courses = []
    return render_template('dashboard.html', page='Dashboard', user=current_user, courses=user_courses)


@app.route('/profile')
@login_required
def profile():
    return render_template('accounts/profile.html', page='Profile', user=current_user)


@app.route('/create')
@login_required
def create_lab():
    form = LabForm()
    return render_template('instructor/create.html', page='Create Lab', user=current_user, form=form)


@app.route('/manage', methods=['GET', 'POST'])
def manage_labs():
    form = LabForm()
    if request.method == 'POST':
        if current_user.is_authenticated:
            name = request.form['name']
            image = request.form['lab-photo']
            with open(image, "rb") as f:
                encoded_image = Binary(f.read())
            tags = []
            for tag in request.form['tags'].split(',').trim():
                tags.append(tag)
            total_page_count = request.form['total-page-count']
            pages = []
            for i in range(1, total_page_count+1):
                file_name = request.form['fileUpload-1' + str(i)]

                page = {
                    'title': request.form['title-p' + str(i)],
                    'details': request.form['details-p' + str(i)],
                }
    return render_template('instructor/manage.html', page='Manage Labs', user=current_user)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
