from flask_login import UserMixin
from main_mod import db, manager
import os


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Article %r>' % self.idpythn


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def getReadableByteSize(num, suffix='B') -> str:
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_fInfo(x):
    fStat = x.stat()
    fByte = getReadableByteSize(fStat.st_size)
    pFile = x.name
    return {'name': x.name, 'size': fByte, 'path': pFile}