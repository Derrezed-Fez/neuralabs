from neuralabs.forms import *
from neuralabs.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, request, redirect, url_for
from mongoengine.queryset.visitor import Q
from neuralabs.__init__ import app
import datetime
import base64
import bson
from bson.binary import Binary
import string
import random
from flask import abort, jsonify
import base64
from scoringEngine import ScoringEngine
from mongoengine.queryset.visitor import Q


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404_not_found.html'), 404


@app.errorhandler(403)
def page_unauthorized(e):
    return render_template('errors/403_unauthorized.html'), 403


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            existing_email = User.objects(email=form.email.data).first()
            existing_username = User.objects(username=form.name.data).first()
            if existing_username:
                form.errors['username'] = ['Username is already in use.']
            if existing_email:
                form.errors['email'] = ['Email is already in use.']
            if not existing_email and not existing_username:
                hash_pass = generate_password_hash(form.password.data, method='pbkdf2:sha256:80000')
                new_user = User(name=form.name.data, email=form.email.data, password=hash_pass)
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
    if current_user.is_authenticated:
        if current_user.is_admin:
            user_courses = Course.objects.all()
        else:
            user_courses = Course.objects(Q(students__contains=current_user) | Q(instructors__contains=current_user))
        labs = Lab.objects()
        return render_template('dashboard.html', page='Dashboard', user=current_user, courses=user_courses, labs=labs)
    else:
        return abort(403, description="User must login.")


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = JoinForm()
    if request.method == 'POST':
        join_code = request.form.get('join_code')
        if join_code:
            course = Course.objects(join_code=join_code).first()
            if course:
                course.update(push__students=current_user.id)
            else:
                form.errors['invalid'] = ['Join code does not exist.']
    enrolled_courses = Course.objects(students__contains=current_user.id)
    instructor_courses = Course.objects(instructors__contains=current_user.id)
    schools = School.objects.all()
    return render_template('accounts/profile.html', page='Profile', user=current_user, form=form,
                           enrolled_courses=enrolled_courses, instructor_courses=instructor_courses, schools=schools)


@app.route('/change_setting', methods=['POST'])
@login_required
def change_setting():
    if request.method == 'POST':
        setting = request.form.get('setting')
        value = request.form.get('value')
        if setting == 'setting_school':
            if value == 'None':
                current_user.update(unset__school=True)
            else:
                school = School.objects(id=value).first()
                if school:
                    current_user.school = school
        if setting == 'setting_private':
            current_user.private = value == 'true'
        current_user.save()

    return app.response_class(response={'status': 'success'}, status=200, mimetype='application/json')


@app.route('/create-lab', methods=['GET', 'POST'])
@login_required
def create_lab():
    form = LabForm()
    tags = Tag.objects.all()

    if request.method == 'POST' and current_user.is_authenticated and form.validate_on_submit():
        total_page_count = int(request.form.get('total-page-count', 0))
        pages = []
        for i in range(1, total_page_count):
            page = {
                'title': request.form[f'title-p{i}'],
                'details': request.form[f'details-p{i}'],
                'hash': request.form.get(f'score_engine_value_{i}', None),
                'points': int(request.form.get(f'score_engine_points_{i}', 0))
            }
            pages.append(page)

        lab = Lab(
            name=request.form['name'],
            default_thumbnail=request.form['thumbnail'],
            date_created=datetime.datetime.now,
            difficulty=request.form['difficulty'],
            description=request.form['description'],
            pages=pages,
            owner=current_user.id,
            course=request.form.get('course', None)
        )
        lab.save()
        if request.files and 'lab-photo' in request.files:
            image = request.files['lab-photo']
            lab.update(custom_thumbnail=base64.b64encode(image.read()))
        return redirect('/manage')

    courses = Course.objects(instructors__contains=current_user.id)
    return render_template('labs/create_lab.html', page='Create Lab', user=current_user, form=form, courses=courses,
                           tags=tags)


@app.route('/manage', methods=['GET'])
def manage_labs():
    labs = Lab.objects(owner=current_user.id)

    course_filter = request.values.get('filter', 'all')
    if course_filter != 'all':
        course = Course.objects(id=course_filter).first()
        if course:
            labs = labs.filter(course=course)

    courses = Course.objects(instructors__contains=current_user.id)
    return render_template('labs/manage.html', page='Manage Labs', user=current_user, labs=labs, courses=courses,
                           filter=course_filter)


@app.route('/edit-lab/<lab_id>', methods=['GET', 'POST'])
def edit_lab(lab_id):
    form = LabForm()

    if current_user.is_authenticated:
        lab = Lab.objects(id=lab_id).first()
        tags = Tag.objects.all()
        if lab.owner == current_user or current_user.is_admin:
            if request.method == "POST" and form.validate_on_submit():
                image = request.files['lab-photo']
                encoded_image = base64.b64encode(image.read())
                total_page_count = int(request.form['total-page-count'])
                pages = []
                for i in range(1, total_page_count + 2):
                    file_attachments = list()
                    for key, value in request.form.items():
                        if 'fileUpload' in key:
                            file_attachments.append(value)
                    page = {
                        'title': request.form[f'title-p{i}'],
                        'details': request.form[f'details-p{i}'],
                        'hash': request.form[f'score_engine_value_{i}'],
                        'points': int(request.form.get(f'score_engine_points_{i}', 0)),
                        'files': file_attachments
                    }
                    pages.append(page)
                lab.update(
                    name=request.form['name'],
                    default_thumbnail=request.form['thumbnail'],
                    custom_thumbnail=encoded_image,
                    date_created=datetime.datetime.now,
                    difficulty=request.form['difficulty'],
                    description=request.form['description'],
                    pages=pages,
                    owner=current_user.id,
                    course=request.form.get('course', None)
                )
                return redirect('/manage')
            return render_template('labs/create_lab.html', lab=lab, user=current_user, page='Edit Lab', form=form,
                                   tags=tags)
    return abort(403, description="User must login.")


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        abort(403, description='User does not have permission to access.')

    courses = Course.objects.all()
    tags = Tag.objects.all()
    schools = School.objects.all()

    return render_template('administration/admin.html', page='Admin', user=current_user, course_form=CourseForm(),
                           courses=courses, tag_form=TagForm(), tags=tags, school_form=SchoolForm(), schools=schools)


@app.route('/create_course', methods=['POST'])
@login_required
def create_course():
    form = CourseForm()
    if request.method == 'POST' and form.validate_on_submit() and current_user.is_admin:
        new_course = Course(name=form.name.data)
        new_course.join_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        new_course.save()
        return redirect(url_for('admin'))


@app.route('/create_tag', methods=['POST'])
@login_required
def create_tag():
    form = TagForm()
    if request.method == 'POST' and form.validate_on_submit() and current_user.is_admin:
        new_tag = Tag(name=form.name.data)
        new_tag.save()
        return redirect(url_for('admin'))


@app.route('/create_school', methods=['POST'])
@login_required
def create_school():
    form = SchoolForm()
    if request.method == 'POST' and form.validate_on_submit() and current_user.is_admin:
        new_school = School(name=form.name.data)
        new_school.save()
        return redirect(url_for('admin'))


@app.route('/course/<course_id>')
@login_required
def manage_course(course_id):
    course = Course.objects(id=course_id).first()
    if not course:
        abort(404, description='Course not found.')

    has_perms = current_user.is_admin or current_user in course.instructors

    if has_perms and request.values.get('remove'):
        course.update(pull__students=request.values.get('remove'))
        return redirect(url_for('manage_course', course_id=course_id))

    if has_perms and request.values.get('select_user'):
        user = User.objects(id=request.values.get('select_user')).first()
        if user:
            course.update(pull__students=user)
            course.update(push__instructors=user)
        return redirect(url_for('manage_course', course_id=course_id))

    if has_perms and request.values.get('remove_instructor'):
        course.update(pull__instructors=request.values.get('remove_instructor'))
        return redirect(url_for('manage_course', course_id=course_id))

    return render_template('administration/course.html', page='Course', user=current_user, course=course,
                           has_perms=has_perms)


@app.route('/delete_course/<course_id>')
@login_required
def delete_course(course_id):
    if current_user.is_admin:
        Course.objects(id=course_id).first().delete()
    return redirect('/admin')


@app.route('/delete_school/<school_id>')
@login_required
def delete_school(school_id):
    if current_user.is_admin:
        School.objects(id=school_id).first().delete()
    return redirect('/admin')


@app.route('/delete_tag/<tag_id>')
@login_required
def delete_tag(tag_id):
    if current_user.is_admin:
        Tag.objects(id=tag_id).first().delete()
    return redirect('/admin')


@app.route('/search_users')
@login_required
def search_users():
    if current_user.is_admin:
        query = request.values.get('q')
        if query:
            users = User.objects(name__icontains=query).only('id', 'name', 'school')
            return jsonify(users)


@app.route('/tags')
@login_required
def search_tags():
    query = request.values.get('q')
    if query:
        tags = Tag.objects(name__icontains=query).only('id', 'name')
    else:
        tags = Tag.objects.all().only('id', 'name')
    return jsonify(tags)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/scores', methods=['GET'])
@login_required
def grade_book():
    user_courses = Course.objects.all()
    return render_template('scores.html', page='Scores', user=current_user, courses=user_courses)


@app.route('/lab/<lab_id>', methods=['GET'])
@login_required
def take_lab(lab_id):
    lab = Lab.objects(id=lab_id).first()
    return render_template('/labs/take-lab.html', user=current_user, lab=lab)


@app.route('/lab-complete', methods=['POST'])
@login_required
def lab_complete():
    if request.method == 'POST':
        if current_user.is_authenticated:
            lab = Lab.objects(id=request.form.get('lab_id')).first()
            modified_answers = dict()
            counter = 1
            for key, value in request.form.items():
                if key != 'lab_id':
                    modified_answers['page' + str(counter)] = value
            engine = ScoringEngine(scoring_type='comparison', answers=modified_answers, key=lab.pages)
            points = engine.calculateScore()
            completion_time = datetime.datetime.now()
            attempt = LabAttempt(time_submitted=completion_time, answers=[modified_answers], points=points,
                                 fk_student=current_user.id)
            attempt.save()

            return render_template('accounts/lab-complete.html',
                                   lab_completion_time=completion_time.strftime("%m/%d/%Y, %H:%M:%S"), points=points,
                                   user=current_user)
        else:
            return abort(403, description="User is not authenticated.")
