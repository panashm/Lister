from flask_script import Manager

from app import app, db, lm, admin, BaseView, expose, ModelView, bcrypt, views

manager = Manager(app)

@manager.command
def update():
    views.update_loans()

if __name__ == "__main__":
    manager.run()