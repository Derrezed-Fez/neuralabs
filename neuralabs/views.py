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
import random, os
from flask import abort, jsonify
import base64
from scoringEngine import ScoringEngine, lookup_points
from mongoengine.queryset.visitor import Q
from werkzeug.utils import secure_filename


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404_not_found.html', error=e), 404


@app.errorhandler(403)
def page_unauthorized(e):
    return render_template('errors/403_unauthorized.html', error=e), 403


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            existing_email = User.objects(email=form.email.data).first()
            existing_username = User.objects(name=form.name.data).first()
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
    return render_template('accounts/register.html', page='Register', form=form, schools=School.objects.all())


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
    return render_template('accounts/reset_password.html', page='Reset Password', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_authenticated:
        if current_user.is_admin:
            user_courses = Course.objects.all()
        else:
            user_courses = Course.objects(Q(students__contains=current_user.id) | Q(instructors__contains=current_user.id))
        labs = Lab.objects()
        print(labs)
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


def save_pages(lab):
    image = request.files['lab-photo']
    if image:
        lab.update(custom_thumbnail=base64.b64encode(image.read()))
    file_dir = f"{os.getcwd()}{app.config['UPLOAD_FOLDER']}/{lab.id}"
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)

    total_page_count = int(request.form.get('total-page-count', 0))
    for i in range(1, total_page_count + 1):
        files = list()
        for attached_file in request.files.keys():
            if f'p{i}' in attached_file:
                if attached_file and request.files[attached_file].filename:
                    filename = secure_filename(request.files[attached_file].filename)
                    filepath = f"{os.getcwd()}{app.config['UPLOAD_FOLDER']}/{lab.id}/{filename}"
                    if not os.path.exists(filepath):
                        request.files[attached_file].save(filepath)
                    files.append(filename)
        lab.pages.append({
            'page_num': i,
            'title': request.form[f'title-p{i}'],
            'details': request.form[f'details-p{i}'],
            'answer_prompt': request.form[f'score_engine_prompt_{i}'],
            'answer': request.form[f'score_engine_value_{i}'],
            'difficulty': request.form[f'answer_difficulty_{i}'],
            'points': lookup_points(request.form[f'answer_difficulty_{i}']),
            'files': files
        })
        lab.save()


@app.route('/create-lab', methods=['GET', 'POST'])
@login_required
def create_lab():
    if not current_user.is_authenticated:
        return abort(403, description="User must login.")

    form = LabForm()
    tags = Tag.objects.all()
    courses = Course.objects(instructors__contains=current_user.id)

    if request.method == 'POST' and form.validate_on_submit():
        lab = Lab(
            name=request.form['name'],
            default_thumbnail=request.form['thumbnail'],
            date_created=datetime.datetime.now,
            difficulty=request.form['difficulty'],
            description=request.form['description'],
            owner=current_user.id,
            course=request.form.get('course', None),
            pages=[]
        )
        lab.save()
        save_pages(lab)

        return redirect('/manage')
    return render_template('labs/create_lab.html', page='Create Lab', user=current_user, form=form, courses=courses,
                           tags=tags)


@app.route('/edit-lab/<lab_id>', methods=['GET', 'POST'])
def edit_lab(lab_id):
    if not current_user.is_authenticated:
        return abort(403, description="User must login.")
    lab = Lab.objects.get(id=lab_id)
    if not lab:
        return abort(404, description="Lab does not exist.")

    form = LabForm()
    tags = Tag.objects.all()
    courses = Course.objects(instructors__contains=current_user.id)

    if request.method == 'POST' and form.validate_on_submit():
        lab.update(
            name=request.form['name'],
            default_thumbnail=request.form['thumbnail'],
            difficulty=request.form['difficulty'],
            description=request.form['description'],
            course=request.form.get('course', None),
        )
        lab.save()
        save_pages(lab)

        return redirect('/manage')
    return render_template('labs/create_lab.html', page='Create Lab', user=current_user, form=form, courses=courses,
                           tags=tags, lab=lab)


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
        new_course.join_code = ''.join(random.choice(string.ascii_uppercase) for _ in range(6))
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
        user = User.objects(id=request.values.get('remove')).first()
        if user:
            course.update(pull__students=user)
        return redirect(url_for('manage_course', course_id=course_id))

    if has_perms and request.values.get('select_user'):
        user = User.objects(id=request.values.get('select_user')).first()
        if user:
            course.update(pull__students=user)
            course.update(push__instructors=user)
        return redirect(url_for('manage_course', course_id=course_id))

    if has_perms and request.values.get('remove_instructor'):
        user = User.objects(id=request.values.get('remove_instructor')).first()
        if user:
            course.update(pull__instructors=user)
        return redirect(url_for('manage_course', course_id=course_id))

    return render_template('administration/course.html', page='Course', user=current_user, course=course,
                           has_perms=has_perms)


@app.route('/delete_lab/<lab_id>')
@login_required
def delete_lab(lab_id):
    lab = Lab.objects(id=lab_id).first()
    if current_user.is_admin or lab.owner.id == current_user.id:
        lab.delete()
    return redirect('/manage')


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
            users = User.objects(name__icontains=query).only('id', 'name', 'school')  # School name nonfunctional
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

    if 'attempt' in request.values:
        attempt_id = request.values.get('attempt')
        if attempt_id == 'new':
            current_attempt = LabAttempt(lab=lab, user=current_user.id, time_started=datetime.datetime.now)
            current_attempt.save()
            return redirect(f"/lab/{lab.id}/{current_attempt.id}")

    attempts = LabAttempt.objects(lab=lab, user=current_user.id)
    current_attempt = LabAttempt.objects(lab=lab, time_submitted=None, user=current_user.id).first()
    return render_template('labs/start_lab.html', user=current_user, lab=lab, attempts=attempts, page=lab.name,
                           current_attempt=current_attempt)


@app.route('/lab/<lab_id>/<attempt_id>', methods=['GET', 'POST'])
@login_required
def continue_lab(lab_id, attempt_id):
    lab = Lab.objects(id=lab_id).first()
    current_attempt = LabAttempt.objects(id=attempt_id, user=current_user.id).first()
    if not current_attempt or not lab:
        return abort(404, description="Lab Attempt Not Found.")
    if current_attempt.time_submitted:  # Lab has already been submitted
        return redirect(f'/results/{lab.id}/{current_attempt.id}')

    page_number = int(request.values.get('page', current_attempt.current_page))
    if page_number <= 0 or page_number > len(lab.pages):
        return abort(404, description="Page Not Found.")

    if request.method == 'POST':
        # Save page results here
        #
        #

        if 'Next Page' in request.form['goto_page']:
            page_number += 1
        if 'Previous Page' in request.form['goto_page']:
            page_number -= 1
        if 'Submit Lab' in request.form['goto_page']:
            current_attempt.time_submitted = datetime.datetime.now
            current_attempt.save()
            return redirect(f'/results/{lab.id}/{current_attempt.id}')

        current_attempt.current_page = page_number
        current_attempt.save()
        return redirect(f'/lab/{lab.id}/{current_attempt.id}?page={page_number}')

    return render_template('labs/take_lab.html', user=current_user, lab=lab, current_attempt=current_attempt,
                           page=lab.name, lab_page=lab.pages[page_number - 1], page_number=page_number,
                           total_pages=len(lab.pages))


@app.route('/results/<lab_id>/<attempt_id>', methods=['GET'])
@login_required
def lab_complete(lab_id, attempt_id):
    lab = Lab.objects(id=lab_id).first()
    attempt = LabAttempt.objects(id=attempt_id, user=current_user.id).first()
    if not attempt or not lab:
        return abort(404, description="Lab Attempt Not Found.")

    # Score attempt
    return render_template('labs/lab_complete.html', attempt=attempt, user=current_user, points=5)
