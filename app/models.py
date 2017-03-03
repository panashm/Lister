from app import db, bcrypt

import datetime, time

from config import WHOOSH_ENABLED

enable_search = WHOOSH_ENABLED
if enable_search:
    import flask_whooshalchemy as whooshalchemy


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, unique=False)
    last_name = db.Column(db.String(64), index=True, unique=True)
    item = db.Column(db.String(140))
    duration = db.Column(db.Integer, index=True)
    dueDate = db.Column(db.DateTime)
    create_date = db.Column(db.DateTime)
    days_remaining = db.Column(db.Integer)
    tech = db.Column(db.String(64))

    def __repr__(self):
        return '<Entry %r>' % (self.first_name)
    
    #def __init__(self, first_name, last_name, body):
     #   self.first_name=first_name
    #  self.last_name = last_name
       # self.body = body
        
    def getPrintableDueDate(self):
        return self.dueDate.strftime('%d/%m/%Y')
    
    def getPrintableCreateDate(self):
        return self.create_date.strftime('%d/%m/%Y')
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    password = db.Column('password', db.LargeBinary(60), nullable=False)
    email = db.Column('email', db.String(50),unique=True , index=True)
    authenticated = db.Column('authenticated', db.Boolean)
    
    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the id to satisfy Flask-Login's requirements."""
        return unicode(self.id)

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False