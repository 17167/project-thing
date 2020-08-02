#13/03/2020
#Jayden Ling
#Web app project

from flask import Flask, render_template, redirect, url_for, request, session, flash, abort, g
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os                       

app = Flask(__name__)
app.database = "project.db"

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
            flash('You need to log in first.') #if user is not logged in and tries to access account page, makes it so they HAVE to login first.
            return redirect(url_for('login'))
    return wrap

#welcome/home page
@app.route('/', methods=['GET', 'POST'])
def welcome():
    return render_template('welcome.html')

#login page fo logins
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        getdb = connect_db().cursor()
        user = request.form["username"] #selects username input
        password = request.form["password"] #selects password input
        sql_list = "SELECT Username,Password,ID FROM Users WHERE Username = ?" #searches for user/password/ID from database
        getdb.execute(sql_list, (user,))
        correct = getdb.fetchone()
        if correct: 
            results = correct[1] #checks if user exists
            if check_password_hash(results, password):
                session['logged_in'] = correct[2] #checks is password relating to user is correct
                results = correct[0]
                flash("Welcome to your task board {}!".format(results))
                return redirect('/account') #redirects to account page
        error = "Invalid Credentials. Try Again." #if user credentials are wrong or does not exit, returns error
    return render_template('login.html', error=error)

#signup page for signup stuff
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
        sql = "SELECT Username FROM Users where Username = ?" #sees if requested username is in db already
        getdb.execute(sql, (new_user,))
        if bool(getdb.fetchall()):
            error = "Username is taken, please find a new one" #if username is already in db, asks users to input a new one
            return render_template("signup.html", error=error)
        sql = "INSERT INTO Users(Username, Password) VALUES (?,?)" #puts whatever user's username/password is into database
        getdb.execute(sql,(new_user, generate_password_hash(new_password, "sha256"))) #encrypts users password via sha256 method and stores into database
        connect_db().commit()  #redirects user to account page after signing up
        flash("Thanks for signing up!") #flashes user friendly message
        return redirect(url_for("login")) #directs them to login screen for quick access
    return render_template("signup.html")

#account page for users to add stuff to their todo list
@app.route('/account', methods=["GET", "POST"])
@login_required
def account():
    if request.method == "GET":
        user_id = session["logged_in"] 
        getdb = connect_db() #connects to db
        cur = getdb.execute('SELECT Tasks.ID,Tasks.Task,Tasks.UserID, Tasks.Completed FROM Tasks JOIN Users ON Users.ID = Tasks.UserID WHERE Users.ID = ?', (user_id,)) #selects tasks user has made
        problem = [dict(ID=row[0],Task=row[1], complete=row[3]) for row in cur.fetchall()] #displays tasks relating to user
        return render_template('account.html', problem=problem)
    return render_template("account.html")

#adding tasks
@app.route('/addtask', methods=["POST"])
def add():
    if request.method == "POST":
        user_id = session["logged_in"]
        new_task = request.form["newtask"]
        getdb = connect_db().cursor()
        if len(new_task) > 100: #ensures task cannot be too big
            flash("Please enter a shorter task!") 
            return redirect("/account")
        if new_task == "" or new_task.isspace(): #ensures task cannot be empty or blank spaces
            flash("Please enter a valid task!") 
            return redirect("/account")
        sql = "INSERT INTO Tasks(Task,UserID) VALUES (?,?)" #inserts new task into db alongside user it is connected to
        getdb.execute(sql, (new_task,user_id,))
        connect_db().commit() #commits changes
    return redirect("/account")

#when clicked checkboxes
@app.route('/checkTask', methods=["POST"])
def check_task():
    if request.method == "POST":
        getdb = connect_db().cursor()
        task = int(request.form["taskid"])
        sql = "UPDATE Tasks SET Completed = 1 WHERE ID = ?" #when checkbox has been clicked, strikes through task
        getdb.execute(sql,(task,))    
        connect_db().commit()
    return redirect('/account')

#deleting tasks
@app.route('/delete', methods=["POST"])
@login_required
def delete():
    if request.method == "POST":
        getdb = connect_db().cursor()
        task = int(request.form["taskid"])
        sql = "DELETE FROM Tasks WHERE ID=?" #finds the ID related to task user wants to delete
        getdb.execute(sql,(task,))    
        connect_db().commit()
    return redirect("/account")

#settings page, won't have much functions yet.
@app.route('/settings')
@login_required
def settings():
    user_id = session["logged_in"]
    return render_template("settings.html")

#logs user out, redirects them to welcome/home page
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None) #sets user session to none, effectively logging out user
    flash('You were just logged out!')
    return redirect(url_for('welcome'))

#incase of error, enters debugging mode
if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)