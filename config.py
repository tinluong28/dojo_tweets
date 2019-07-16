from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'kldjrs.sdfu9u3m4lkjdfgu0'
bcrypt = Bcrypt(app)
