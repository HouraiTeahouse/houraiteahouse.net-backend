import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from houraiteahouse.app import app
from houraiteahouse.models import db

# Flask migrate scripting for SQLAlchemy

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    if not os.path.exists('/var/htwebsite'):
        os.makdirs('/var/htwebsite')
        print('Make sure to set up the /var/htwebsite secretkey and mysqlcreds files!')
    if not os.path.exists('/var/htwebsite/news'):
        os.makdirs('/var/htwebsite/news')
        # Spin up some quick language dirs
        os.makedirs('/var/htwebsite/news/en')  # English
        os.makedirs('/var/htwebsite/news/ja')  # Japanese
    db.create_all()


@manager.command
def drop_db():
    db.drop_all()


@manager.command
def create_admin():
    # Temporary for initialization - as part of this, connect to the DB &
    # create a real admin
    db.session.add(User(email='ad@min', password='admin', admin=True))
    db.session.commit()


@manager.command
def create_data():
    pass

if __name__ == '__main__':
    manager.run()
