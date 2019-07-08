from flask import Flask, flash, render_template, redirect, request, session
from mysqlconnection import MySQLConnection
from flask_bcrypt import Bcrypt
import re
from datetime import date

app = Flask(__name__)
app.secret_key = 'kldjrs.sdfu9u3m4lkjdfgu0'
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASS_REGEX = re.compile(r'^((?=.*\d)(?=.*[A-Z])(?=.*\W).{8,16})$')
NAME_REGEX = re.compile(r'^[a-zA-Z_-]+$')

# colculate age in years


@app.route('/test')
def test():
    return "running"


@app.route('/registration')
def registration():
    return render_template('index.html')


@app.route('/signup', methods=['POST'])
def signup():
    mysql = MySQLConnection('basic_registration')

    def calculateAge(birthdate):
        days_in_year = 365.2425
        bday_list = birthdate.split('-')
        bday = date(int(bday_list[0]), int(bday_list[1]), int(bday_list[2]))
        age = int((date.today() - bday).days / days_in_year)
        return age
    age = calculateAge(request.form['birthday'])
    print(age)
    is_valid = True
    if len(request.form['fname']) < 1:
        is_valid = False
        flash('First name is required', 'errors')
    if not NAME_REGEX.match(request.form['fname']):
        is_valid = False
        flash('First name must contain all letters', 'errors')
    if len(request.form['lname']) < 1:
        is_valid = False
        flash('Last name is required', 'errors')
    if not NAME_REGEX.match(request.form['lname']):
        is_valid = False
        flash('Last name must contain all letters', 'errors')
    if age < 10:
        is_valid = False
        flash('You must be at least 10 years old to register', 'errors')
    if len(request.form['password']) < 5:
        is_valid = False
        flash('Password should be at least 5 characters', 'errors')
    elif not PASS_REGEX.match(request.form['password']):
        is_valid = False
        flash('Password must contain at least a number and special character, upper and lowercase', 'errors')
    elif request.form['password'] != request.form['confirmpass']:
        is_valid = False
        flash('Confirm password must match with password', 'errors')
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Invalid email address!", 'errors')
    if is_valid:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        query = 'INSERT INTO users (first_name, last_name, birthday, email, pw_hash) VALUES(%(fname)s, %(lname)s, %(bday)s, %(email)s, %(pw_hash)s);'
        data = {'fname': request.form['fname'],
                'lname': request.form['lname'],
                'bday': request.form['birthday'],
                'email': request.form['email'],
                'pw_hash': pw_hash}
        new_user_id = mysql.query_db(query, data)
        session['userID'] = new_user_id
        return redirect('/success')
        # flash('Registered successfully', 'success')
    return redirect('/registration')


@app.route('/login', methods=['POST'])
def login():
    mysql = MySQLConnection('basic_registration')
    query = "SELECT * FROM users WHERE users.email = %(email)s;"
    data = {'email': request.form['email']}
    user = mysql.query_db(query, data)
    print(user)
    if user:
        if bcrypt.check_password_hash(user[0]['pw_hash'], request.form['password']):
            session['userID'] = user[0]['id']
            return redirect('/success')
    flash('You could not be logged in. Try again!', 'login error')
    return redirect('/registration')


@app.route('/success')
def success():
    if session:
        return render_template('success.html')
    return redirect('/registration')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/registration')


if __name__ == "__main__":
    app.run(debug=True)
