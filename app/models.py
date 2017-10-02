from app import db, bcrypt

import datetime, time

from config import WHOOSH_ENABLED

enable_search = WHOOSH_ENABLED
if enable_search:
    import flask_whooshalchemy as whooshalchemy


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, unique=False)
    last_name = db.Column(db.String(64), index=True, unique=False)
    quantity = db.Column(db.Integer)
    item = db.Column(db.String(140))
    asset = db.Column(db.String(140))
    duration = db.Column(db.Integer, index=True)
    dueDate = db.Column(db.DateTime)
    create_date = db.Column(db.DateTime)
    days_remaining = db.Column(db.Integer)
    date_returned = db.Column(db.String(140))
    status = db.Column(db.String(140))
    tech = db.Column(db.String(64))
    notes = db.Column(db.String(160))

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
    
#class ItemChoices(db.model):
    

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, unique=False)
    last_name = db.Column(db.String(64), index=True, unique=False)
    item = db.Column(db.String(140))
    action = db.Column(db.String(140))
    tech = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    
    def getPrintableDueDate(self):
        return self.date.strftime('%d/%m/%y')

class adminEmails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    adminEmail = db.Column('adminemail', db.String(50),unique=True , index=True)
    notifEmail = db.Column('noteemail', db.String(50),unique=True , index=True)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    password = db.Column('password', db.String(60), nullable=False)
    email = db.Column('email', db.String(50),unique=True , index=True)
    authenticated = db.Column('authenticated', db.Boolean)
    confirmed = db.Column(db.Boolean, nullable=True, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    
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