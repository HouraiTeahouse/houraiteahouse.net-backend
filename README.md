[![Discord](https://discordapp.com/api/guilds/151219753434742784/widget.png)](https://discord.gg/VuZhs9V)
[![Build Status](https://travis-ci.org/HouraiTeahouse/houraiteahouse.net-backend.svg?branch=master)](https://travis-ci.org/HouraiTeahouse/houraiteahouse.net-backend)
[![Coverage Status](https://coveralls.io/repos/github/HouraiTeahouse/houraiteahouse.net-backend/badge.svg)](https://coveralls.io/github/HouraiTeahouse/houraiteahouse.net-backend)

# Hourai Teahouse Website Backend

This is the backend package for the Hourai Teahouse website.  Thus far it was written with a "get pieces working" mindset rather than a proper design/plan and thus it requires significant cleanup & improvement.

## Setup

To get started, you will need to install python 3.5 or newer.

You can set up the backend in your working environment or create a virtual
environment for the backend that is isolated from your current environment.
If you do not wish to use a virtual environment, you can skip to the
installation steps below.

If you choose to use a virtual environment, you will have to install the
virtualenv utility and use it to create a environment that uses Python 3.5.
Then, activate the environment and continue with the installation steps below.

Installation Steps:
1. Install pip for python 3.
2. Use `pip install -r requirements.txt` to install the relevant dependencies.
3. Append the absolute path of src/houraiteahouse to the PYTHONPATH environment
variable.

### Setting up the database

* Setup/configure mysql (or whatever compatible DMBS you are using instead).
* Create the file "secretkey" in /var/htwebsite. It simply needs to exist. 
* Create the file "news" in /var/htwebsite. It simply needs to exist.
* Create the file "mysqlcreds" in /var/htwebsite. In this file, on three
separate lines, specify, in this order: DBMS username, DBMS password, DBMS
database name.
* You may be able to use `manage.py create_db` and other options to simplify this process.
* Run `manage.py db init` to initialize the Flask migrations directory
* Run `manage.py db migrate` to generate DB config from models
* Run `manage.py db upgrade` to commit changes to the database

NOTE: If you have problems running the `manage.py` commands, make sure the file
permissions and privilege escalation is correct such that the backend can login
to the database, and access any files it needs.

### Running the server

To run the server, you have a few options:

* Execute src/run.py - use this option if you are planning to modify the backend, as it will automatically pick up changes.
* Set up uWSGI using the provided config (eg, uwsgi --master --ini [path to houraiteahouse_uwsgi.ini] and ensure the ini file and nginx config point to the correct paths
* Set up uWSGI to autorun via Emperor or a similar option

## Contributing

Before checking in code, please ensure you have cleaned up pycache or any other autogenerated files.  Please do not check in any socket created by uWSGI.

## Major TODOs:

* Heavy refactoring (remove duplicate code, DB caching, etc)
* Additional features (wiki, issue tracker, etc)
