#13/03/2020
#Jayden Ling
#Web app project

from flask import Flask, render_template, redirect, url_for, request, session, flash, abort
from flask_login import LoginManager, UserMixin
from functools import wraps
import sqlite3
import os
 
app = Flask(__name__)

#login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to log in first.')
            return redirect(url_for('login'))
    return wrap

#index page
@app.route('/')
@login_required
def index():
    return render_template("index.html")

@app.route('/home')
def home():
    return "yo"

#login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['password'] != 'password' or request.form['username'] != 'admin':
            error = "Invalid Credentials. Try Again."
        else:
            session['logged_in'] = True
            flash("You're logged in as admin")
            return redirect(url_for('account')) 
    return render_template('login.html', error=error)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/account')
def account():
    if request.method == "GET":
        if 'logged_in' in session:
            return render_template('account.html')
        else:
            return redirect(url_for('login'))
    return render_template('account.html')

#logs user out, redirects them to login page
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('home'))

#incase of error, enters debugging mode
if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)