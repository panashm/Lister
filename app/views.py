from __future__ import print_function # In python 2.7
from flask import render_template, flash, redirect, session, url_for, request, g
from urlparse import urlparse, urljoin
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
 
import sys
from datetime import date, datetime, time, timedelta
import time
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from app import app, db, lm, admin, BaseView, expose, ModelView, bcrypt
from .forms import searchForm, newEntryForm, item_choices, day_choices, search_choices, loginForm
from .models import Entry, User, Log

class MyView(BaseView):
    @expose('/')
    def index(self):
        
        return self.render('AdminIndex.html')
        
admin.add_view(MyView(name='Hello'))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Entry, db.session))
admin.add_view(ModelView(Log, db.session))

currDate = time.strftime("%d/%m/%Y")
#print ("dd/mm/yyyy format =  %s/%s/%s" % (dueDate.day, dueDate.month, dueDate.year), file=sys.stderr )

def update_loans():
    entries = Entry.query.all()
    if entries:
        d1 = datetime.strptime(currDate, '%d/%m/%Y')
        for entry in entries:

            if (entry.dueDate != None):
                dueDate = (entry.dueDate)
                dueDate = dueDate.strftime('%d/%m/%Y')
                #currDate = time.strftime(dueDate, "%d/%m/%Y")
                print (dueDate, file=sys.stderr)
                d2 = datetime.strptime(dueDate, '%d/%m/%Y')
                daysRemaining = ((d2 - d1).days)
                print ("yah yah yah yah yah",file=sys.stderr)
                print(daysRemaining, file=sys.stderr)
                print(entry.first_name, file=sys.stderr)

                if daysRemaining >= 0: 
                    entry.days_remaining = int(daysRemaining)
                else:
                    daysRemaining = 0
                    entry.days_remaining = int(daysRemaining)

                #if entry.days_remaining == 0:
                    #sendEmail(entry)

                db.session.commit()

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
            form = newEntryForm(request.form)
            #flash('Record was successfully added')
            print(form.firstName, file=sys.stderr)
            integer = int(form.item.data)
            item_display = item_choices[integer][1]

            day_integer = int(form.duration.data) + 1
            day_display = int(day_choices[day_integer - 1][1])
            
            currrDate = datetime.strptime(currDate, '%d/%m/%Y')
            due_date = datetime.strptime(currDate, '%d/%m/%Y') + timedelta(days=day_integer)

            #if form.validate():
            print(day_display, file=sys.stderr)
            print("hello there", file=sys.stderr)
            print("the date is:", day_integer, due_date, file=sys.stderr)

            if (item_display == "Other"):
                entry = Entry(first_name=form.firstName.data, last_name=form.lastName.data, item = form.body.data, duration = day_display, dueDate = due_date, 
                              days_remaining = day_display, create_date = currrDate, tech=g.user.username)
            else:
                entry = Entry(first_name=form.firstName.data, last_name=form.lastName.data, item = item_display, duration = day_display, dueDate = due_date, 
                              days_remaining = day_display, create_date = currrDate, tech=g.user.username)

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

def sendEmail( entry ):
    
    fromaddr = "list3rapp@gmail.com"
    toaddr = current_user.email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Loan Due Notification"

    body = "The loan for a " + entry.item + " by " + entry.first_name + " " + entry.last_name + " is now due, please follow this up."
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "Pan34bel")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

    print("email has been sent")
    return
    
@app.route('/delete', methods=['POST'])
def delete_entry():
    if request.method == 'POST':
        entry = Entry.query.get(request.form['entry_to_delete'])
        print("we are printing", file=sys.stderr)
        print(entry.first_name, file=sys.stderr)
        log = Log(first_name=entry.first_name, last_name=entry.last_name, item = entry.item, action = "Deleted", tech = entry.tech, date = datetime.strptime(currDate, '%d/%m/%Y')) 
        db.session.add(log)
        Entry.query.filter_by(id=request.form['entry_to_delete']).delete()
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
            results = Entry.query.filter((Entry.first_name.contains(form1.searchField.data)) | (Entry.last_name.contains(form1.searchField.data))).all()
        elif search_cat == "Item":
            results = Entry.query.filter(Entry.item.contains(form1.searchField.data)).all()
        elif search_cat == "Tech":
            results = Entry.query.filter(Entry.tech.contains(form1.searchField.data)).all()
        elif search_cat == "Days Remaining":
            results = Entry.query.filter(Entry.days_remaining.contains(form1.searchField.data)).all()
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
            if bcrypt.check_password_hash(user.password, form.password.data):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=False)
                flash('Logged in successfully.')
                next = request.args.get('next')
                # is_safe_url should check if the url is safe for redirects.
                # See http://flask.pocoo.org/snippets/62/ for an example.
                #if not is_safe_url(next):
                print ("got hhsdgq43tqaesereeee")

                return redirect(next or url_for('main'))
               # return redirect("/")
    next = request.args.get('next')
    print ("got hereeee")
    return render_template("login.html", form=form, next=next)

@app.route("/history", methods=["GET"])
def history():

    return render_template("history.html", logs = Log.query.all())

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