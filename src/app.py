from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import requests

#Mappers
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import select
from sqlalchemy import create_engine
from mongoengine import *


#Connect mongodb
connect('testdb')

#Local class
from forms import Login, SearchForm
from company import Companies

app = Flask(__name__)  # Setting up the flask application

# MySQL Database and SQLAlchemy configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql9224878:4sLR1fLK9s@sql9.freemysqlhosting.net/sql9224878'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine('mysql+pymysql://sql9224878:4sLR1fLK9s@sql9.freemysqlhosting.net/sql9224878', echo=True)
conn = engine.connect()

# Instatiating the application
db = SQLAlchemy(app)

# User Mapper Class (SQLAlchemy)
class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column('id', db.Integer, primary_key = True)
    username = db.Column('username', db.Unicode)
    password = db.Column('password', db.Unicode)

    # Inserting via ORM
    def __init__(self, id, username, password):
        db.id = id
        db.username = username
        db.password = password


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('LoginPage'))
    return wrap


#Login
@app.route('/', methods = ['GET','POST'])
def LoginPage():
    message = ""
    form = Login(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        s = select([Users])
        result = conn.execute(s)
        validation = result.fetchone()
        if username == validation[1] and password == validation[2]:
            session['logged_in'] = True
            return redirect(url_for('search'))
        else:
            return render_template('home.html', form = form, message = 'Invalid Credentials')
    return render_template('home.html', form = form)


#Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('LoginPage'))


#Search
@app.route('/search', methods = ['GET','POST'])
@is_logged_in
def search():

    form = SearchForm(request.form)
    if request.args.get('search'):
        search = request.args.get('search')
        page = int(request.args.get('page',1))
        url = "http://localhost:9200/chrunchbase/company/_search"
        querystring = {"q":search, "size":10, "from": (page*10)-10}
        response = requests.request("GET", url, params=querystring)
        data = response.json()
        total_pages = int(data["hits"]["total"]/10) + 1
        return render_template('search.html', form=form, hits = data["hits"]["total"], result = data["hits"]["hits"], q = search, pages = [i for i in range(1,total_pages+1)])

    return render_template('search.html', form=form)


#Company Details
@app.route('/company/<string:id>/')
@is_logged_in
def details(id):
    company = company.objects.get(id = id)
    print(company.description)
    return render_template('company_details.html', result = company)


if __name__ == '__main__' :
    app.secret_key='demo123'
    app.run(host='0.0.0.0', port=5000,debug = True)
