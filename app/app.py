from __future__ import print_function # In python 2.7
import sys
from flask import (Flask, flash, render_template, request, redirect, url_for)
from flask_sqlalchemy import SQLAlchemy
import datetime, time


from flask_wtf import Form
from wtforms import TextField, PasswordField, validators, HiddenField
from wtforms import TextAreaField, BooleanField, SelectField
from wtforms.validators import Required, EqualTo, Optional
from wtforms.validators import Length, Email
from wtforms.widgets import TextArea
#from .momentjs import momentjs
#app.jinja_env.globals['momentjs'] = momentjs

app = Flask(__name__)
app.debug = True
app.config.from_object('config')
db = SQLAlchemy(app)

from models import *

item_choices = [ (0, 'VGA Adapter'),(1, 'Apple Superdrive'),(2, 'T430'), (3, 'Other') ]
day_choices = [ (0, '1'),(1, '2'),(2, '3'), (3, '4'), (4, '5'),(5, '6'), (6, '7') ]

currDate = time.strftime("%d/%m/%Y")
#print ("dd/mm/yyyy format =  %s/%s/%s" % (dueDate.day, dueDate.month, dueDate.year), file=sys.stderr )
                        
class newEntryForm(Form):
    firstName = TextField('Enter first Name:', validators=[Required()])
    lastName = TextField('Enter last Name:', validators=[Required()])
    body = TextField(u'Text', widget=TextArea(), validators=[Required()])
    item = SelectField('Select Item:',
                            [validators.Required()],
                            choices=item_choices)
    duration = SelectField('Duration (Days):',
                            [validators.Required()],
                            choices=day_choices)

@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        form = newEntryForm(request.form)
        #flash('Record was successfully added')
        print(form.firstName, file=sys.stderr)
        integer = int(form.item.data)
        item_display = item_choices[integer][1]
        
        day_integer = int(form.duration.data)
        day_display = day_choices[day_integer][1]
        
        due_date = datetime.datetime.strptime(currDate, '%d/%m/%Y') + datetime.timedelta(days=day_integer)

        #if form.validate():
        print(item_display, file=sys.stderr)
        print("hello there", file=sys.stderr)
        
        if (item_display == "Other"):
            entry = Entry(first_name=form.firstName.data, last_name=form.lastName.data, item = form.body.data, duration = day_display, dueDate = due_date, days_remaining = day_display)
        else:
            entry = Entry(first_name=form.firstName.data, last_name=form.lastName.data, item = item_display, duration = day_display, dueDate = due_date, days_remaining = day_display)
            
        db.session.add(entry)
        db.session.commit()
            
        flash('Record was successfully added')

        return render_template('index.html', form = newEntryForm(), entries = Entry.query.all())
       # else:
        #return render_template('index.html', form = form)
        
        
    #Calculate the days remaining
    entries = Entry.query.all()
    d1 = datetime.datetime.strptime(currDate, '%d/%m/%Y')
    for entry in entries:
        
        if (entry.dueDate != None):
            dueDate = (entry.dueDate)
            dueDate = dueDate.strftime('%d/%m/%Y')
            #currDate = time.strftime(dueDate, "%d/%m/%Y")
            print (dueDate, file=sys.stderr)
            d2 = datetime.datetime.strptime(dueDate, '%d/%m/%Y')
            daysRemaining = abs((d2 - d1).days)
            print ("yah yah yah yah yah",file=sys.stderr)
            print(daysRemaining, file=sys.stderr)
            print(entry.first_name, file=sys.stderr)
            
            
            entry.days_remaining = daysRemaining
            db.session.commit()
    
    
    return render_template('index.html', form = newEntryForm(), entries = Entry.query.all())

@app.route('/delete', methods=['POST'])
def delete_entry():
    if request.method == 'POST':
        Entry.query.filter_by(id=request.form['entry_to_delete']).delete()
        db.session.commit()
        
    return redirect(url_for('main'))

if __name__ == "__main__":
    app.run()
    
