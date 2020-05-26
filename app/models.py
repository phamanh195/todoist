from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from datetime import date, datetime
import hashlib
from itertools import groupby
from operator import attrgetter


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(64))
    confirmed = db.Column(db.Boolean, default=False)
    firstname = db.Column(db.String(64))
    lastname = db.Column(db.String(64))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    notes = db.relationship('Note', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.member_since:
            self.member_since = datetime.utcnow()
        if self.email is not None and self.avatar_hash is None \
                and self.confirmed:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    def get_notes(self, date):
        return self.notes.filter_by(timestamp=date).all()
    
    @property
    def group_by_notes(self):
        notes = self.notes.order_by(Note.timestamp.desc()).all()
        notes = groupby(notes, attrgetter('timestamp'))
        return notes
    
    @staticmethod
    def completion_rate(notes):
        if not isinstance(notes, list):
            notes = list(notes)
        try:
            rate = sum(1 for note in notes if note.status) * 100 // len(notes)
        except ZeroDivisionError:
            rate = 0
        return rate
    
    # Set, check, update Password
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')
    
    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    # Confirm, change, update Email
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')
    
    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True
    
    # Set avatar
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating
        )
    
    def __repr__(self):
        return '<User %r>' % self.username


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    status = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.Date, default=date.today, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))