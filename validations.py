from flask import flash
import re
from datetime import date
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASS_REGEX = re.compile(r'^((?=.*\d)(?=.*[A-Z])(?=.*\W).{8,16})$')
NAME_REGEX = re.compile(r'^[a-zA-Z_-]+$')


def calculateAge(birthdate):
    days_in_year = 365.2425
    bday_list = birthdate.split('-')
    bday = date(int(bday_list[0]), int(bday_list[1]), int(bday_list[2]))
    age = int((date.today() - bday).days / days_in_year)
    return age


def validate_signup(form):
    is_valid = True
    age = 0
    if form['birthdate']:
        age = calculateAge(form['birthdate'])
    if len(form['fname']) < 1:
        is_valid = False
        flash('First name is required', 'errors')
    if not NAME_REGEX.match(form['fname']):
        is_valid = False
        flash('First name must contain all letters', 'errors')
    if len(form['lname']) < 1:
        is_valid = False
        flash('Last name is required', 'errors')
    if not NAME_REGEX.match(form['lname']):
        is_valid = False
        flash('Last name must contain all letters', 'errors')
    if age < 10:
        is_valid = False
        flash('You must be at least 10 years old to register', 'errors')
    if len(form['password']) < 5:
        is_valid = False
        flash('Password should be at least 5 characters', 'errors')
    elif not PASS_REGEX.match(form['password']):
        is_valid = False
        flash('Password must contain at least a number and special character, upper and lowercase', 'errors')
    elif form['password'] != form['confirmpass']:
        is_valid = False
        flash('Confirm password must match with password', 'errors')
    if not EMAIL_REGEX.match(form['email']):
        is_valid = False
        flash("Invalid email address!", 'errors')
    if is_valid == False:
        return False
    if is_valid:
        return True


def validate_tweet(form):
    is_valid = True
    if len(form['tweet']) < 5 or len(form['tweet']) > 255:
        is_valid = False
        flash('Tweets must be between 5 and 225 charaters', 'errors')
    if is_valid:
        return True
    else:
        return False
