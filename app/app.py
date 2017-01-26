from __future__ import print_function # In python 2.7
import sys
from flask import (Flask, flash, render_template, request, redirect, url_for)
from flask_sqlalchemy import SQLAlchemy


from flask_wtf import Form
from wtforms import TextField, PasswordField, validators, HiddenField
from wtforms import TextAreaField, BooleanField, SelectField
from wtforms.validators import Required, EqualTo, Optional
from wtforms.validators import Length, Email
from wtforms.widgets import TextArea

app = Flask(__name__)
app.debug = True
app.config.from_object('config')
db = SQLAlchemy(app)

from models import *

class newEntryForm(Form):
    firstName = TextField('Enter first Name:', validators=[Required()])
    lastName = TextField('Enter last Name:', validators=[Required()])
    body = TextField(u'Text', widget=TextArea(), validators=[Required()])
    item = SelectField('Select Item:',
                            [validators.Required()],
                            choices=[
                                (1, 'VGA Adapter'),
                                (2, 'Apple Superdrive'),
                                (3, 'T430'),
                                (4, 'Other'),
                            ])

@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        form = newEntryForm(request.form)
        #flash('Record was successfully added')
        print(form.firstName, file=sys.stderr)

        #if form.validate():
            #print('Hello wssorld!', file=sys.stderr)

        entry = Entry(first_name=form.firstName.data, last_name=form.lastName.data, body = form.body.data)
            
        db.session.add(entry)
        db.session.commit()
            
        flash('Record was successfully added')

        return render_template('index.html', form = newEntryForm(), entries = Entry.query.all())
       # else:
        #return render_template('index.html', form = form)
    return render_template('index.html', form = newEntryForm(), entries = Entry.query.all())

@app.route('/delete', methods=['POST'])
def delete_entry():
    if request.method == 'POST':
        Entry.query.filter_by(id=request.form['entry_to_delete']).delete()
        db.session.commit()
        
    return redirect(url_for('main'))

if __name__ == "__main__":
    app.run()
    
