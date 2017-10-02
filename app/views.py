from __future__ import print_function # In python 2.7
from flask import render_template, flash, redirect, session, url_for, request, g
from urlparse import urlparse, urljoin
import smtplib, re
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import sys
from sqlalchemy import cast
from sqlalchemy.sql.expression import cast
from sqlalchemy import Column, Integer, Sequence, types, Float, String

import sqlalchemy
from datetime import date, datetime, time, timedelta
import pytz
from flask.ext.mail import Message
from pytz import timezone
import time
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from app import app, db, lm, admin, BaseView, expose, ModelView, bcrypt, mail, SQLAlchemy
from .forms import searchForm, newEntryForm, item_choices, day_choices, search_choices, loginForm, registrationForm
from .models import Entry, User, Log, adminEmails
from itsdangerous import URLSafeTimedSerializer

class MyView(BaseView):
    @expose('/')
    def index(self):
        
        return self.render('AdminIndex.html')
        
admin.add_view(MyView(name='Welcome'))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Entry, db.session))
admin.add_view(ModelView(adminEmails, db.session))

sydney = timezone('Australia/Sydney')
au_time = datetime.now(sydney)

currDate = au_time.strftime("%d/%m/%Y %H:%M:%S")

#print ("dd/mm/yyyy format =  %s/%s/%s" % (dueDate.day, dueDate.month, dueDate.year), file=sys.stderr )

allEmails = adminEmails.query.all()
if allEmails:
    adminEmail = allEmails[0].adminEmail
    notifEmail = allEmails[0].notifEmail

    print(adminEmail, notifEmail)
def lower(string):
    return string.lower()

def update_loans():
    entries = Entry.query.all()
    if entries:
        au_time = datetime.now(sydney)
        currDate = au_time.strftime("%d/%m/%Y %H:%M:%S")
        d1 = datetime.strptime(currDate, '%d/%m/%Y %H:%M:%S')
        d1 = d1.date()
        for entry in entries:

            if (entry.dueDate != None):
                dueDate = (entry.dueDate)
                dueDate = dueDate.strftime('%d/%m/%Y %H:%M:%S')
                
                #currDate = time.strftime(dueDate, "%d/%m/%Y")
                print (d1, dueDate, file=sys.stderr)
                d2 = datetime.strptime(dueDate, '%d/%m/%Y %H:%M:%S')
                d2 = d2.date()
                
                print(d1,d2)
                daysRemaining = ((d2 - d1).days)
                print ("Testing",file=sys.stderr)
                print(entry.days_remaining, daysRemaining, file=sys.stderr)
                print(entry.first_name, file=sys.stderr)

                if daysRemaining >= 0: 
                    entry.days_remaining = int(daysRemaining)
                else:
                    daysRemaining = 0
                    entry.days_remaining = int(daysRemaining)

                #if entry.days_remaining == 0:

                db.session.commit()
    sendEmailEntry()

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.before_request
def before_request():
    if current_user.is_authenticated:
        g.user = None # return username in get_id()
        print("its authentic")
    else:
        g.user = current_user
        print("its something")
        
    #if current_user.id:
     #   print("found an id")

@lm.user_loader
def user_loader(id):
    print ("the id is:")
    print (id, file=sys.stderr)
    user = User.query.get(id)
    if user:
        print ("User found for")
        print(user.id, file=sys.stderr)
        return User.query.get(int(id))
    else:
        print ("We got here instead")
        return None

@app.context_processor
def inject_user():
    if current_user.is_authenticated:
        return dict(user=user_loader(current_user.id))
    else:
        user = "hello"
        return dict(user=current_user)
    
@app.route("/", methods=['GET', 'POST'])
@login_required
def main():
    #user = user_loader(current_user.id)
    if current_user.is_authenticated:
        g.user = user_loader(current_user.id)
        print ("the user is:")
        print (g.user.id, file=sys.stderr)
    if request.method == 'POST':
        if request.form['btn'] == 'Submit':
            au_time = datetime.now(sydney)

            currDate = au_time.strftime("%d/%m/%Y %H:%M:%S")
            form = newEntryForm(request.form)
            #flash('Record was successfully added')
            print(form.firstName, file=sys.stderr)
            integer = int(form.item.data)
            item_display = item_choices[integer][1]
            print("Hello there")
            day_integer = int(form.duration.data) 
            print("the day integer is:", day_integer)
            day_display = day_integer #need to fix this
            print("the day display is:", day_display)

            currrDate = datetime.strptime(currDate, '%d/%m/%Y %H:%M:%S')
            due_date = datetime.strptime(currDate, '%d/%m/%Y %H:%M:%S') + timedelta(days=day_integer)

            #if form.validate():
            print(day_display, file=sys.stderr)
            print("hello there", file=sys.stderr)
            print("the date is:", day_integer, due_date, file=sys.stderr)

            if (item_display == "Other"):
                entry = Entry(first_name=form.firstName.data, last_name=form.lastName.data, quantity=form.quantity.data, item = form.body.data, asset = form.asset.data, duration = day_display, dueDate = due_date, 
                              days_remaining = day_display, create_date = currrDate, status="On Loan", tech=g.user.username,notes = form.notes.data)
            else:
                entry = Entry(first_name=form.firstName.data, last_name=form.lastName.data, quantity=form.quantity.data, item = item_display,asset = form.asset.data, duration = day_display, dueDate = due_date, 
                              days_remaining = day_display, create_date = currrDate, status="On Loan", tech=g.user.username, notes = form.notes.data)

            db.session.add(entry)
            db.session.commit()

            flash('Record was successfully added')

            return redirect(url_for('main'))           # else:
            #return render_template('index.html', form = form)
        else:
            return render_template('viewEntry.html', user = g.user, entries = Entry.query.all())
    else:
        #Calculate the days remaining
        #update_loans()
                
    
        return render_template('index.html', user = g.user, form = newEntryForm(), entries = Entry.query.all())

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

def sendEmailConfirm(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=("List3r", app.config['MAIL_DEFAULT_SENDER'])
        )
    mail.send(msg)
    
def sendEmailEntry():
    
    results = Entry.query.filter(cast(Entry.days_remaining, sqlalchemy.String).ilike("%"+ "0" +"%"), Entry.status.ilike("%"+ "On Loan" +"%")).all()
    if results:
        subject = "Service Desk Loans Due"
        
        msg = Message(
            subject,
            recipients=[notifEmail],
            html = render_template('loanDue.html', entries=results),
            sender=("List3r", app.config['MAIL_DEFAULT_SENDER'])
            )
        mail.send(msg)

        print("email has been sent")
        flash("update email sent")
    else:     
        print("theres no loans due")


@app.route('/delete', methods=['POST'])
def delete_entry():
    g.user = user_loader(current_user.id)

    if request.method == 'POST':
        entry = Entry.query.get(request.form['entry_to_delete'])
        entry.status = "Returned"
        date = datetime.strptime(currDate, '%d/%m/%Y %H:%M:%S')
        date = date.strftime('%d/%m/%Y')
        entry.date_returned = str(date) + ", " + str(g.user.username)
        entry.days_remaining = 0
        print("we are printing", file=sys.stderr)
        print(entry.first_name, file=sys.stderr)
        #log = Log(first_name=entry.first_name, last_name=entry.last_name, item = entry.item, action = "Deleted", tech = entry.tech, date = datetime.strptime(currDate, '%d/%m/%Y')) 
        #db.session.add(log)
        #Entry.query.filter_by(id=request.form['entry_to_delete']).delete()
        db.session.commit()
        
    return redirect(url_for('main'))

@app.route('/Entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def view_entry(entry_id):
    print("the page is")
    print (request.referrer, file=sys.stderr)
    print (request.endpoint, file=sys.stderr)
    fetched_entry=Entry.query.filter_by(id=entry_id).first()
    print(fetched_entry.first_name, file=sys.stderr)
    return render_template('viewEntry.html', entry=fetched_entry, prevPage = request.referrer)

@app.route('/Search/', methods=['GET', 'POST'])
@login_required
def search_entry():
    if request.method == 'POST':
        form1 = searchForm(request.form)
        
        integer = int(form1.category.data)
        search_cat = search_choices[integer][1]
        
        print("GOING IN", file=sys.stderr)
        print(form1.searchField.data, file=sys.stderr)
        if search_cat == "iD":
            results = Entry.query.filter_by(id=form1.searchField.data).all()
        elif search_cat == "Client":
            results = Entry.query.filter((Entry.first_name.ilike("%"+ form1.searchField.data +"%")) | (Entry.last_name.ilike("%"+ form1.searchField.data +"%")) ).all()
        elif search_cat == "Item":
            results = Entry.query.filter(Entry.item.ilike("%"+ form1.searchField.data +"%")).all()
        elif search_cat == "Asset":
            results = Entry.query.filter(Entry.asset.ilike("%"+ form1.searchField.data +"%")).all()
        elif search_cat == "Tech":
            results = Entry.query.filter(Entry.tech.ilike("%"+ form1.searchField.data +"%")).all()
        elif search_cat == "Days Remaining":
            results = Entry.query.filter(cast(Entry.days_remaining, sqlalchemy.String).ilike("%"+ form1.searchField.data +"%")).all()
        else:
            results = []
        
        return render_template('searchEntry.html', form = searchForm(), results = results)
    else:
        return render_template('searchEntry.html', form = searchForm())

if __name__ == "__main__":
    app.run()
    

@app.route("/login", methods=["GET", "POST"])
def login():
    """For GET requests, display the login form. For POSTS, login the current user
    by processing the form."""
    #print dbprint("Username is:")

    form = loginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        print("Username is:")
        print(user.username)
        print("password is:")
        print(user.password)
        if len(user.password) < 25:
            user.set_password(user.password)
        
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data) and user.authenticated == True:
                #user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=False)
                flash('Logged in successfully.')
                next = request.args.get('next')
                # is_safe_url should check if the url is safe for redirects.
                # See http://flask.pocoo.org/snippets/62/ for an example.
                #if not is_safe_url(next):
                print ("got ere")

                return redirect(next or url_for('main'))
               # return redirect("/")
    next = request.args.get('next')
    print ("got hereeee")
    return render_template("login.html", form=form, next=next)

@app.route("/history", methods=["GET"])
def history():
    return redirect(url_for('main'))
    #return render_template("history.html", logs = Log.query.all())
    
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

@app.route("/verifyMessage", methods=["GET"])
def verifyMessage():
    """Message asking them to check their emails"""
    return render_template("checkEmail.html")

@app.route("/confirmed", methods=["GET"])
def confirmed():
    """account confirmed"""
    return render_template("activated.html")

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = registrationForm()
    """
    user = User(
        email=form.email.data,
        password=form.password.data,
        confirmed=False
        )

    """
    
    if request.method == "POST" and form.validate():
            #must be knox email address
            usernameF  = form.username.data
            emailF = form.email.data
            passwordF = form.password.data
            passwordF = bcrypt.generate_password_hash(passwordF).decode('utf-8')
            domain = re.search(r'@\w+(.*)', emailF).group()
            print("the domain is:", domain)

            #check if user exists
            checkUsername = User.query.filter_by(username=usernameF)
            checkEmail = User.query.filter_by(email=emailF)
            if checkUsername.count() > 0 or checkEmail.count() > 0 or hasNumbers(emailF) or domain != "@knox.nsw.edu.au":
                if checkUsername.count() > 0:
                    flash("That username is already taken, please choose another")
                    return render_template('signup.html', form=form, message="Username taken")
                elif checkEmail.count() > 0:
                    flash("That email is already taken, please choose another")
                    return render_template('signup.html', form=form, message="Email taken")
                else:
                    flash("Use knox email address")
                    return render_template('signup.html', form=form, message="Please use Knox email")
            else:
                #enter user into database
                user = User(username=usernameF, password = passwordF, email = emailF, authenticated = False, confirmed = False)
                token = generate_confirmation_token(user.email)

                flash("Thanks for registering!")
                
                confirm_url = url_for('confirm_email', token=token, _external=True)
                html = render_template('activate.html', confirm_url=confirm_url)
                subject = "Please confirm your email"
                
                sendEmailConfirm(emailF, subject, html)
                
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('verifyMessage'))
    else:
        flash("didnt specify validation")
        
    return render_template("signup.html", form=form)
 
    
@app.route("/logout", methods=["GET"])
def logout():
    """Logout the current user."""
    print("user logged out eyyy")
    #user = current_user
    #user.authenticated = False
    #db.session.add(user)
    #db.session.commit()
    logout_user()
    return redirect(url_for('main')) 


@app.route("/confirm/<token>", methods=["GET"])
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        user.authenticated = True
        user.confirmed_on = au_time 
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
        
    return redirect(url_for('confirmed'))