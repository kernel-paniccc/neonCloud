from flask_login import UserMixin
from main_mod import db, manager
import random
import string


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Article %r>' % self.idpythn


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def get_readable_byte_size(num, suffix='B') -> str:
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_info(x):
    fstat = x.stat()
    fbyte = get_readable_byte_size(fstat.st_size)
    pfile = x.name
    return {'name': x.name, 'size': fbyte, 'path': pfile}


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string
