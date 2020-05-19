#13/03/2020
#Jayden Ling
#Web app project

from flask import Flask, render_template, redirect, url_for, request, session, flash, abort
from flask_login import LoginManager, UserMixin
import sqlite3
import os
 
app = Flask(__name__)
login = LoginManager(app)

@app.route('/')
def home():
    if not session.get('logged in'):
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True 
    else:
        flash('Incorrect Credentials')
    return home()

#incase of error, enters debugging mode
if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)