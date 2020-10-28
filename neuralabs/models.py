from flask_login import UserMixin
from neuralabs.__init__ import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()


class User(UserMixin, db.Document):
    meta = {'collection': 'User'}
    name = db.StringField(max_length=30)
    email = db.StringField(max_length=30)
    password = db.StringField()
    roles = db.ListField(default=['Student'])
    join_date = db.DateTimeField()

class Lab(UserMixin, db.Document):
    meta = {'collection': 'Lab'}
    name = db.StringField(max_length=30)
    tags = db.ListField(defualt=[])
    date_created = db.DateTimeField()
