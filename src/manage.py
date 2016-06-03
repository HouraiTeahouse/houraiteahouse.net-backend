from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from houraiteahouse.app import app, db
from houraiteahouse.authentication.user import User

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.command
def create_db():
    db.create_all()

@manager.command
def drop_db():
    db.drop_all()
    
@manager.command
def create_admin():
    # Temporary for initialization - as part of this, connect to the DB & create a real admin
    db.session.add(User(email='ad@min', password='admin', admin=True))
    db.session.commit()

@manager.command
def create_data():
    pass

if __name__ == '__main__':
    manager.run()
