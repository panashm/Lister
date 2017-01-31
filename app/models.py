from app import db

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True, unique=False)
    last_name = db.Column(db.String(64), index=True, unique=True)
    item = db.Column(db.String(140))
    duration = db.Column(db.Integer, index=True)
    dueDate = db.Column(db.DateTime)
    days_remaining = db.column(db.Integer)

    def __repr__(self):
        return '<Entry %r>' % (self.first_name)
    
    #def __init__(self, first_name, last_name, body):
     #   self.first_name=first_name
    #  self.last_name = last_name
       # self.body = body