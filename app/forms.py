from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf import Form
from wtforms import TextField, PasswordField, validators, HiddenField
from wtforms import TextAreaField, BooleanField, SelectField, IntegerField
from wtforms.validators import Required, EqualTo, Optional, NumberRange
from wtforms.validators import Length, Email
from wtforms.widgets import TextArea

item_choices = [ (0, 'VGA Adapter'),(1, 'Apple Superdrive'),(2, 'T430'), (3, 'Mac Charger'), (4, 'Other') ]
search_choices = [ (0, 'Client'),(1, 'iD'),(2, 'Item'), (3, 'Tech'), (4, 'Days Remaining') ]

day_choices = [ (0, '1'),(1, '2'),(2, '3'), (3, '4'), (4, '5'),(5, '6'), (6, '7') ]

class newEntryForm(Form):
    firstName = TextField('Enter first Name:', validators=[Required()])
    lastName = TextField('Enter last Name:', validators=[Required()])
    quantity = TextField('Enter Quantity:', validators=[Required()])
    body = TextField(u'Text', validators=[Required()])
    asset = TextField('Enter Asset No')
    item = SelectField('Select Item:',
                            [validators.Required()],
                            choices=item_choices)
    duration = IntegerField('Enter Quantity:', [validators.Required(), validators.NumberRange(min=0, max=9, message="please enter between 1 and 9")])
    
class searchForm(Form):
    searchField = TextField('Search Term:  ', validators=[Required()])
    category = SelectField('Category:',
                            [validators.Required()],
                            choices=search_choices)
    
class loginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = TextField('Password', validators=[Required()])
    
class registrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password')
   # accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [validators.Required()])