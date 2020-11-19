from flask_login import UserMixin
from neuralabs.__init__ import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()


class User(UserMixin, db.Document):
    roles = {
        'S': ('Student', '#3adb76'),
        'I': ('Instructor', '#1f84ef'),
        'A': ('Admin', '#e3073c')
    }
    meta = {'collection': 'User'}
    name = db.StringField(max_length=30)
    email = db.StringField(max_length=30)
    password = db.StringField()
    role = db.StringField(max_length=1, choices=roles.keys(), default='S')
    join_date = db.DateTimeField()

    @property
    def is_admin(self):
        return self.role == 'A'

    @property
    def is_student(self):
        return self.role == 'S'

    @property
    def is_instructor(self):
        return self.role == 'I'

    @property
    def role_display(self):
        return self.roles[self.role][0]

    @property
    def role_color(self):
        return self.roles[self.role][1]


class Course(db.Document):
    meta = {'collection': 'Course'}
    title = db.StringField(max_length=50)
    join_code = db.StringField(max_length=6)
    instructors = db.ListField()
    students = db.ListField()
    roles = db.ListField(default=['Student'])
    join_date = db.DateTimeField()

class Lab(UserMixin, db.Document):
    meta = {'collection': 'Lab'}
    name = db.StringField(max_length=30)
    image = db.BinaryField()
    tags = db.ListField(defualt=[])
    date_created = db.DateTimeField()
    difficulty = db.StringField()
    description = db.StringField()
    pages = db.ListField(default=[])
    pk_owner = db.ObjectIdField()
