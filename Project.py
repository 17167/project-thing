#13/03/2020
#Jayden Ling
#Web app project

from flask import Flask, render_template, redirect, url_for, request, session, flash, abort, g
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
 
app = Flask(__name__)
app.database = "Users.db"

#connects database to webapp
def connect_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.database)
    return db

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
        getdb = connect_db().cursor()
        user = request.form["username"]
        password = request.form["password"]
        sql_list = "SELECT Username,Password,ID FROM Users WHERE Username = ?"
        getdb.execute(sql_list, (user,))
        correct = getdb.fetchall()[0]
        if len(correct) > 0: 
            results = correct[1]
            if check_password_hash(results, password):
                session['logged_in'] = correct[2]
                results = correct[0]
                flash("Welcome to yo task board {}".format(results))
                return redirect('/account')
        error = "Invalid Credentials. Try Again."
    return render_template('login.html', error=error)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        error = None
        getdb = connect_db().cursor()
        new_user = request.form["newuser"] #gets whatever the username is
        new_password = request.form["newpassword"] #gets whatever the password is
        if new_user == "" or new_password == "": #ensures username/password cannot be blank 
            error = "Enter a valid username or password please"
            return render_template("signup.html", error=error)
        sql = "SELECT Username FROM Users where Username = ?"
        getdb.execute(sql, (new_user,))
        if bool(getdb.fetchall()):
            error = "Username is taken, please find a new one" #if username is already in db, asks users to input a new one
            return render_template("signup.html", error=error)
        sql = "INSERT INTO Users(Username, Password) VALUES (?,?)" #puts whatever user's username/password is into database
        getdb.execute(sql,(new_user, generate_password_hash(new_password, "sha256")))
        connect_db().commit()
        flash("You're all signed up!")
        return redirect(url_for('login'))
    return render_template('signup.html')

#account page for users to add stuff to their todo list
@app.route('/account', methods=["GET", "POST"])
@login_required
def account():
    if request.method == "GET":
        user_id = session["logged_in"]
        getdb = connect_db()
        cur = getdb.execute('SELECT Task FROM Tasks JOIN Users ON Users.ID = Tasks.UserID WHERE Users.ID = ?', (user_id,))
        problem = [dict(Task=row[0]) for row in cur.fetchall()]
        return render_template('account.html', problem=problem)
    return render_template("account.html")

@app.route('/addtask', methods=["POST"])
def add():
    if request.method == "POST":
        user_id = session["logged_in"]
        new_task = request.form["newtask"]
        getdb = connect_db().cursor()
        #if new_task == "":
           #error = "Please enter a valid task!"
        sql = "INSERT INTO Tasks(Task,UserID) VALUES (?,?)"
        getdb.execute(sql, (new_task,user_id,))
        connect_db().commit()
    return redirect("/account")

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