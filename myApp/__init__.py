
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager



app = Flask(__name__)

# set a secret key to protect from things like modifying cookies and CSRF attacks
# the key was made using the secrets module in python
# secrets.token_hex(16) created a 16-Byte random string  key 
app.config['SECRET_KEY'] = '8b37ecc045767c15ff1c927ef3d93948'  # later on, this should be turned into an environmental variable
# config SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# This import needs to happen after the creation of app and db
from myApp import routes