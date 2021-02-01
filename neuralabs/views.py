from neuralabs.forms import *
from neuralabs.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, request, redirect, url_for
from neuralabs.__init__ import app
import datetime
import base64
import bson
from bson.binary import Binary
import string
import random
from flask import abort, jsonify

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
    if current_user.is_authenticated:
        labs = Lab.objects()
        return render_template('dashboard.html', page='Dashboard', user=current_user, courses=user_courses)
    else:
        return render_template('unauthorized.html')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = JoinForm()
    if request.method == 'POST':
        join_code = request.form.get('join_code')
        if join_code:
            course = Course.objects(join_code=join_code).first()
            if course:
                course.update(push__students=str(current_user.id))
            else:
                form.errors['invalid'] = ['Join code does not exist.']
    enrolled_courses = Course.objects(students__contains=str(current_user.id))
    instructor_courses = Course.objects(instructors__contains=str(current_user.id))
    return render_template('accounts/profile.html', page='Profile', user=current_user, form=form,
                           enrolled_courses=enrolled_courses, instructor_courses=instructor_courses)


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
            image = request.files['lab-photo']
            encoded_image = base64.b64encode(image.read())
            tags = []
            for tag in request.form['tags'].split(','):
                tags.append(tag.strip())
            total_page_count = int(request.form['total-page-count'])
            print(request.form)
            pages = []
            for i in range(1, total_page_count+2):
                file_attachments = list()
                for key, value in request.form.items():
                    if 'fileUpload' in key:
                        file_attachments.append(value)
                page = {
                    'title': request.form['title-p' + str(i)],
                    'details': request.form['details-p' + str(i)],
                    'files': file_attachments
                }
                pages.append(page)
            lab = Lab(request.form['name'], encoded_image, tags, datetime.datetime.now, request.form['difficulty'],
                    request.form['description'], pages, current_user.id)
            lab.save()
    labs = Lab.objects(pk_owner__contains=str(current_user.id))
    print(labs)
    return render_template('instructor/manage.html', page='Manage Labs', user=current_user, labs=labs)

@app.route('/edit-lab', methods=['GET', 'POST'])
def edit_lab():
    if current_user.is_authenticated:
        if request.method == 'GET':
            lab_id = request.args.get('id')
            lab = Lab.objects(id__contains=str(lab_id))[0]
            lab['tags'] = ', '.join(lab['tags'])
        elif request.method == "POST":
            image = request.files['lab-photo']
            encoded_image = base64.b64encode(image.read())
            tags = []
            for tag in request.form['tags'].split(','):
                tags.append(tag.strip())
            total_page_count = int(request.form['total-page-count'])
            print(request.form)
            pages = []
            for i in range(1, total_page_count+2):
                file_attachments = list()
                for key, value in request.form.items():
                    if 'fileUpload' in key:
                        file_attachments.append(value)
                page = {
                    'title': request.form['title-p' + str(i)],
                    'details': request.form['details-p' + str(i)],
                    'files': file_attachments
                }
                pages.append(page)
            db.Lab.update({'_id': request.form['id']}, {'$set': {'tags': tags, 'name': request.form['name'],
                'image': image, 'difficulty': request.form['difficulty'], 'description': request.form['description'],
                'pages': pages}})
        return render_template('instructor/edit_lab.html', lab=lab, user=current_user)
    else:
        return render_template('unautherized.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        abort(403, description='User does not have permission to access.')
    form = CourseForm()
    if request.method == 'POST':
        if form.validate_on_submit() and current_user.is_admin:
            new_course = Course(title=form.title.data)
            new_course.join_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            new_course.save()
            return redirect(url_for('admin'))
    courses = Course.objects.all()
    return render_template('administration/admin.html', page='Admin', user=current_user, form=form, courses=courses)


@app.route('/course/<course_id>')
@login_required
def manage_course(course_id):
    course = Course.objects(id=course_id).first()
    if not course:
        abort(404, description='Course not found.')

    students = User.objects(id__in=course.students)
    instructors = User.objects(id__in=course.instructors)
    has_perms = current_user.is_admin or current_user in instructors
    if has_perms and request.values.get('remove'):
        course.update(pull__students=request.values.get('remove'))
        return redirect(url_for('manage_course', course_id=course_id))
    if has_perms and request.values.get('add_instructor'):
        course.update(pull__students=request.values.get('add_instructor'))
        course.update(push__instructors=request.values.get('add_instructor'))
        return redirect(url_for('manage_course', course_id=course_id))
    if has_perms and request.values.get('remove_instructor'):
        course.update(pull__instructors=request.values.get('remove_instructor'))
        return redirect(url_for('manage_course', course_id=course_id))
    return render_template('administration/course.html', page='Course', user=current_user, course=course,
                           students=students, instructors=instructors, has_perms=has_perms)


@app.route('/instructors')
@login_required
def instructors():
    if current_user.is_admin:
        query = request.values.get('q')
        if query:
            instructors = User.objects(role__in=['I', 'A'], name__icontains=query).values_list('id', 'name', 'email')
            return jsonify(instructors)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
