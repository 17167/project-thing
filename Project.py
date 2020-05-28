#13/03/2020
#Jayden Ling
#Web app project

from flask import Flask, render_template, redirect, url_for, request, session, flash, abort, g
from functools import wraps
import sqlite3
import os
 
app = Flask(__name__)
app.database = "Users.db"

#connects sqlite3 to web app
def connect_db():
    return sqlite3.connect(app.database)

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

#welcome/home page
@app.route('/', methods=['GET', 'POST'])
def welcome():
    if request.method == 'POST':
        flash('You were just logged out!')
    return render_template('welcome.html')

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

#account page for users to add stuff to their todo list (at some point)
@app.route('/account')
@login_required
def account():
    if request.method == "GET":
        if 'logged_in' in session:
            g.db = connect_db()
            cur = g.db.execute('select * from Tasks')
            todo = [dict(Task=row[1]) for row in cur.fetchall()]
            return render_template('account.html', todo=todo)
        else:
            return redirect(url_for('login'))
    return render_template('account.html')

#logs user out, redirects them to welcome/home page
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('welcome'))

#incase of error, enters debugging mode
if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)