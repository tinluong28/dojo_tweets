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


@app.route('/users')
def users():
    if session:
        user_mysql = MySQLConnection('dojo_tweets')
        user_query = "SELECT first_name, last_name, id FROM users WHERE users.id = %(userID)s;"
        user_data = {'userID': session['userID']}
        user = user_mysql.query_db(user_query, user_data)
        users_mysql = MySQLConnection('dojo_tweets')
        users_query = f"SELECT * FROM users WHERE users.id != {session['userID']}"
        all_users = users_mysql.query_db(users_query)
        following_users_mysql = MySQLConnection('dojo_tweets')
        following_users_query = f"SELECT GROUP_CONCAT(follows.following_id) as following_id FROM users LEFT JOIN follows ON users.id = follows.user_id WHERE users.id = {session['userID']} GROUP BY users.id;"
        following_users = following_users_mysql.query_db(following_users_query)
        if following_users[0]['following_id']:
            following_id = following_users[0]['following_id'].split(',')
        else:
            following_id = []
        return render_template('users.html', current_user=user[0], all_users=all_users, following_id=following_id)
    return redirect('/registration')


@app.route('/followers')
def followers():
    if session:
        user_mysql = MySQLConnection('dojo_tweets')
        user_query = "SELECT first_name, last_name, id FROM users WHERE users.id = %(userID)s;"
        user_data = {'userID': session['userID']}
        user = user_mysql.query_db(user_query, user_data)
        follower_mysql = MySQLConnection('dojo_tweets')
        follower_query = f"SELECT followers.id, followers.first_name, followers.last_name, followers.email FROM users LEFT JOIN follows ON users.id = follows.following_id LEFT JOIN users as followers ON follows.user_id = followers.id WHERE users.id = {session['userID']};"
        followers = follower_mysql.query_db(follower_query)
        print(followers)
        following_users_mysql = MySQLConnection('dojo_tweets')
        following_users_query = f"SELECT GROUP_CONCAT(follows.following_id) as following_id FROM users LEFT JOIN follows ON users.id = follows.user_id WHERE users.id = {session['userID']} GROUP BY users.id;"
        following_users = following_users_mysql.query_db(following_users_query)
        if following_users[0]['following_id']:
            following_id = following_users[0]['following_id'].split(',')
        else:
            following_id = []
        return render_template('followers.html', current_user=user[0], followers=followers, following_id=following_id)
    return redirect('/registration')


@app.route('/<followed_user>/follow')
def follow(followed_user):
    mysql = MySQLConnection('dojo_tweets')
    query = "INSERT INTO follows (user_id,following_id) VALUES(%(user_id)s, %(following_id)s);"
    data = {'user_id': session['userID'],
            'following_id': followed_user}
    mysql.query_db(query, data)
    return redirect('/users')


@app.route('/<followed_user>/unfollow')
def unfollow(followed_user):
    mysql = MySQLConnection('dojo_tweets')
    query = "DELETE FROM follows WHERE user_id = %(user_id)s AND following_id= %(following_id)s;"
    data = {'user_id': session['userID'],
            'following_id': followed_user}
    mysql.query_db(query, data)
    return redirect('/users')


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
        following_users_mysql = MySQLConnection('dojo_tweets')
        following_users_query = f"SELECT GROUP_CONCAT(follows.following_id) as following_id FROM users LEFT JOIN follows ON users.id = follows.user_id WHERE users.id = {session['userID']} GROUP BY users.id;"
        following_users = following_users_mysql.query_db(following_users_query)
        if following_users[0]['following_id']:
            following_id = following_users[0]['following_id'].split(',')
        else:
            following_id = []
        for tweet in tweets:
            if tweet['liked_by']:
                tweet['liked_by'] = tweet['liked_by'].split(',')
        return render_template('dashboard.html', current_user=user[0], tweets=tweets, following_id=following_id)
    return redirect('/registration')


@app.route('/tweet', methods=['POST'])
def tweet():
    is_valid = True
    if len(request.form['tweet']) < 5 or len(request.form['tweet']) > 255:
        is_valid = False
        flash('Tweets must be between 5 and 225 charaters', 'errors')
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
