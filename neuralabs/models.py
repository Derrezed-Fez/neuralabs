from flask_login import UserMixin
from neuralabs.__init__ import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()


class School(db.Document):
    name = db.StringField()


class User(UserMixin, db.Document):
    roles = {
        'U': ('User', '#3adb76'),
        'A': ('Admin', '#e3073c')
    }
    meta = {'collection': 'User'}
    name = db.StringField(max_length=30)
    email = db.StringField(max_length=30)
    score = db.IntField(default=0)
    password = db.StringField()
    role = db.StringField(max_length=1, choices=roles.keys(), default='U')
    join_date = db.DateTimeField()
    # User Settings:
    private = db.BooleanField(default=False)
    school = db.ReferenceField(School)

    @property
    def is_admin(self):
        return self.role == 'A'

    @property
    def role_display(self):
        return self.roles[self.role][0]

    @property
    def role_color(self):
        return self.roles[self.role][1]

    @property
    def level(self):
        level = self.score / 500  # 500 points per level, might change to exponential
        return level

    @property
    def required_points(self):
        return (self.level + 1) * 500


class Course(db.Document):
    meta = {'collection': 'Course'}
    name = db.StringField(max_length=50)
    join_code = db.StringField(max_length=6)
    instructors = db.ListField(db.ReferenceField(User))
    students = db.ListField(db.ReferenceField(User))
    roles = db.ListField(default=['Student'])
    join_date = db.DateTimeField()


class Tag(db.Document):
    name = db.StringField(max_length=30)


class Lab(UserMixin, db.Document):
    meta = {'collection': 'Lab'}
    name = db.StringField(max_length=30)
    course_id = db.StringField()
    image = db.BinaryField()
    tags = db.ListField(default=[])
    date_created = db.DateTimeField()
    difficulty = db.StringField()
    description = db.StringField()
    pages = db.ListField(default=[])
    owner = db.ReferenceField(User)
    course = db.ReferenceField(Course)

    @property
    def total_points(self):
        return sum([int(page['points']) for page in self.pages])


class LabAttempt(UserMixin, db.Document):
    meta = {'collection': 'LabAttempt'}
    time_submitted = db.DateTimeField()
    answers = db.ListField(default=[])
    points = db.IntField()
    student = db.ReferenceField(User)
    pk_owner = db.ObjectIdField()

    @property
    def course(self):
        return Course.objects(id=self.course_id).first()
