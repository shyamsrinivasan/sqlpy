# Flask Management Application
This package is a [Flask](https://flask.palletsprojects.com/en/2.2.x/) application to read, write and store accounting information to a local database, and manage clients in an accounting firm.

## Features (current version):
* Supports a visually clean web application interface through flask's [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) templating engine and [Bootstrap](https://getbootstrap.com/) CSS for HTML templates
* Supports user login and storage functionality through a login credential manager [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
* Supports use of MySQL database through [SQLAlchemy](https://www.sqlalchemy.org/) to be used for locally storing client information 

## Features (previous versions):
* Addition of data to DB using inputs written in *excel* or *csv* file
* Connecting to an MySQL database (DB) using SQL-python connector
* Use SQLAlchemy instead of Python-SQL Connector to access database

## Python and environment setup:
* Setup a python virutal enviroment in the working directory: `python -m venv flaskenv`
* Use `pip` and the requirements.txt file to setup required packages: `pip install -r requirements.txt`


## List of Tasks:

- [x] Develop an example connecting to an existing MySQL database (DB) using SQL-python connector
- [x] Improve components of DB by adding additional fields
- [x] Enable addition of data to DB using inputs written in *excel* or *csv* file
- [x] Enable data query through python API
- [x] Use SQLAlchemy instead of Python-SQL Connector to access database (to enable use with Flask-SQLAlchemy)
- [] Convert API to a python package before proceeding to app development
- [x] Use a FLASK web app to add GUI functionality 

## Notes:
- Database migration carried out in [flaskapp](https://github.com/shyamsrinivasan/flaskapp)
- Changes need to made in /app/home/models.py in [flaskapp](https://github.com/shyamsrinivasan/flaskapp) for migrations