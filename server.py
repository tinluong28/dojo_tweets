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
    mysql = MySQLConnection('dojo_tweets')

    def calculateAge(birthdate):
        days_in_year = 365.2425
        bday_list = birthdate.split('-')
        bday = date(int(bday_list[0]), int(bday_list[1]), int(bday_list[2]))
        age = int((date.today() - bday).days / days_in_year)
        return age
    age = calculateAge(request.form['birthdate'])
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
        query = 'INSERT INTO users (first_name, last_name, birthdate, email, password) VALUES(%(fname)s, %(lname)s, %(bday)s, %(email)s, %(pw_hash)s);'
        data = {'fname': request.form['fname'],
                'lname': request.form['lname'],
                'bday': request.form['birthdate'],
                'email': request.form['email'],
                'pw_hash': pw_hash}
        new_user_id = mysql.query_db(query, data)
        session['userID'] = new_user_id
        # return redirect('/dashboard')
        if new_user_id:
            flash('Registered successfully. Please log in.', 'success')
        else:
            flash('Unsuccessful. Please try again', 'errors')
    return redirect('/registration')


@app.route('/login', methods=['POST'])
def login():
    mysql = MySQLConnection('dojo_tweets')
    query = "SELECT * FROM users WHERE users.email = %(email)s;"
    data = {'email': request.form['email']}
    user = mysql.query_db(query, data)
    print(user)
    if user:
        if bcrypt.check_password_hash(user[0]['password'], request.form['password']):
            session['userID'] = user[0]['id']
            return redirect('/dashboard')
    flash('You could not be logged in. Try again!', 'login error')
    return redirect('/registration')


@app.route('/dashboard')
def dashboard():
    if session:
        user_mysql = MySQLConnection('dojo_tweets')
        user_query = "SELECT first_name, last_name, id FROM users WHERE users.id = %(userID)s;"
        user_data = {'userID': session['userID']}
        user = user_mysql.query_db(user_query, user_data)
        tweets_mysql = MySQLConnection('dojo_tweets')
        tweets_query = "SELECT tweets.id as tweet_id, tweets.message, users.id as user_id, users.first_name, users.last_name, tweets.created_at, tweets.updated_at, COUNT(likes.id) as num_of_likes, GROUP_CONCAT(likes.user_id) as liked_by FROM tweets LEFT JOIN users ON tweets.user_id = users.id LEFT JOIN likes ON likes.tweet_id = tweets.id GROUP BY message ORDER BY tweets.created_at DESC;"
        tweets = tweets_mysql.query_db(tweets_query)
        for tweet in tweets:
            if tweet['liked_by']:
                tweet['liked_by'] = tweet['liked_by'].split(',')
        return render_template('dashboard.html', current_user=user[0], tweets=tweets)
    return redirect('/registration')


@app.route('/tweet', methods=['POST'])
def tweet():
    is_valid = True
    if len(request.form['tweet']) > 255:
        is_valid = False
        flash('Tweets must be less than 225 charaters', 'errors')
    if is_valid:
        mysql = MySQLConnection('dojo_tweets')
        query = "INSERT INTO tweets (message, user_id) VALUES(%(message)s, %(userID)s);"
        data = {'message': request.form['tweet'],
                'userID': session['userID']}
        new_tweet_id = mysql.query_db(query, data)
    return redirect('/dashboard')


@app.route('/tweets/<tweet_id>/like')
def like_tweet(tweet_id):
    mysql = MySQLConnection('dojo_tweets')
    query = "INSERT INTO likes (user_id, tweet_id) VALUES(%(user_id)s, %(tweet_id)s)"
    data = {'user_id': session['userID'],
            'tweet_id': tweet_id}
    new_like_id = mysql.query_db(query, data)
    return redirect('/dashboard')


@app.route('/tweets/<tweet_id>/unlike')
def unlike_tweet(tweet_id):
    mysql = MySQLConnection('dojo_tweets')
    query = "DELETE FROM likes WHERE likes.tweet_id = %(tweet_id)s AND likes.user_id = %(user_id)s"
    data = {'tweet_id': tweet_id,
            'user_id': session['userID']}
    mysql.query_db(query, data)
    return redirect('/dashboard')


@app.route('/tweets/<tweet_id>/edit')
def edit_tweet(tweet_id):
    if session:
        mysql = MySQLConnection('dojo_tweets')
        query = "SELECT users.id FROM users LEFT JOIN tweets ON users.id = tweets.user_id WHERE tweets.id = %(tweet_id)s;"
        data = {'tweet_id': tweet_id}
        tweet_owner = mysql.query_db(query, data)
        user_mysql = MySQLConnection('dojo_tweets')
        user_query = "SELECT first_name, last_name, id FROM users WHERE users.id = %(userID)s;"
        user_data = {'userID': session['userID']}
        user = user_mysql.query_db(user_query, user_data)
        if session['userID'] == tweet_owner[0]['id']:
            mysql = MySQLConnection('dojo_tweets')
            query = "SELECT message FROM tweets WHERE tweets.id = %(tweet_id)s"
            data = {'tweet_id': tweet_id}
            message = mysql.query_db(query, data)
            return render_template('edit_tweet.html', tweet_id=tweet_id, current_user=user[0], message=message[0]['message'])
        else:
            flash("You can't edit tweet that isn't your own", 'errors')
            return render_template('edit_tweet.html', tweet_id=tweet_id, current_user=user[0], message="")
    return redirect('/registration')


@app.route('/tweets/<tweet_id>/update_tweet', methods=['POST'])
def update_tweet(tweet_id):
    is_valid = True
    if len(request.form['updated_msg']) > 255:
        is_valid = False
        flash('Tweets must be less than 225 charaters', 'errors')
        return redirect('/tweets/<tweet_id>/edit')
    if is_valid:
        mysql = MySQLConnection('dojo_tweets')
        query = "UPDATE tweets SET message = %(message)s WHERE tweets.id = %(tweet_id)s"
        data = {'message': request.form['updated_msg'],
                'tweet_id': tweet_id}
        mysql.query_db(query, data)
    return redirect('/dashboard')


@app.route('/tweets/<tweet_id>/delete')
def delete_tweet(tweet_id):
    mysql = MySQLConnection('dojo_tweets')
    query = "DELETE FROM tweets WHERE tweets.id = %(tweet_id)s;"
    data = {'tweet_id': tweet_id}
    mysql.query_db(query, data)
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/registration')


if __name__ == "__main__":
    app.run(debug=True)
