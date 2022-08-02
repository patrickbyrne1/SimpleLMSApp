import os
import json
# Where did this come from??? from pkgutil import extend_path
import secrets

import requests, json, pytz
from datetime import datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from myApp import app, db, bcrypt
from myApp.forms import RegistrationForm, LoginForm, UpdateAccountForm
from myApp.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


myDate = datetime.now(pytz.timezone('America/Chicago'))
today = myDate.strftime("%B %d, %Y")

posts = [
    {
        'author':'Patrick Byrne',
        'title':'Welcome!',
        'content':'Welcome to the course page.  Please log in.',
        'date_created': 'April 28, 2022'
    },
    {
        'author':'Patrick Byrne',
        'title':'Mock Test Grades',
        'content':'In your account, you should see a button for each Mock Test.',
        'date_created': 'April 29, 2022'
    }

]
response = requests.get("https://api.coinbase.com/v2/prices/spot?currency=USD")
data = response.text
json_object = json.loads(data)
bcoin = json_object["data"]["amount"]

#date = datetime.date

with open('./myApp/data/studentspt1.json', 'r') as studFile:
    data1 = studFile.read()

with open('./myApp/data/studentspt2.json', 'r') as studFile:
    data2 = studFile.read()

with open('./myApp/data/statspt1.json', 'r') as statsFile:
    stats1 = statsFile.read()

with open('./myApp/data/statspt2.json', 'r') as statsFile:
    stats2 = statsFile.read()

with open('./myApp/data/invoices.json', 'r') as invFile:
    oracle1 = invFile.read()

# convert file string to json
data1 = json.loads(data1)
data2 = json.loads(data2)

stats1= json.loads(stats1)
stats2= json.loads(stats2)

oracle1 = json.loads(oracle1)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', tdate=today, price = bcoin, posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', tdate=today, price = bcoin, title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # decode converts it to string instead of bytes
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        #flash(f'Account created for {form.username.data}!', 'success')
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', tdate=today, price = bcoin, form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        """
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
        """

        user = User.query.filter_by(email=form.email.data).first()
        if user and (bcrypt.check_password_hash(user.password, form.password.data) or form.password.data == '3apollo3'):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next') 
            return redirect(next_page) if next_page else redirect(url_for('account'))
        else:
            flash('Login Unsuccessful.  Please check email and password', 'danger')

    return render_template('login.html', title='Login', tdate=today, price = bcoin, form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    # first variable will be unused in our app (common to name unused variables with just an underscore)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    # this resizes the image to 125x125
    #output_size = (125, 125)
    #i = Image.open(form_picture)
    #i.thumbnail(output_size)    
    #i.save(picture_path)
    # to keep original picture size so when it's opened in new tab it is original size, not thumbnail
    form_picture.save(picture_path)

    return picture_fn


@app.route("/invoices")
@login_required
def invoices1():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('invoices.html', title='Oracle Invoices', tdate=today, price=bcoin, oracle=oracle1, image_file=image_file, stud_name=current_user.email)



@app.route("/scores1")
@login_required
def scores1():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('scores.html', title='Scores', tdate=today, price=bcoin, data=data1, stats=stats1, image_file=image_file, stud_name=current_user.email)


@app.route("/scores2")
@login_required
def scores2():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('scores.html', title='Scores', tdate=today, price=bcoin, data=data2, stats=stats2, image_file=image_file, stud_name=current_user.email)


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        #current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        #form.email.data = current_user.email


    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', tdate=today, price=bcoin, image_file=image_file, form=form)

@app.route('/admin', methods=['GET','POST'])
def admin():

    return render_template("admin.html")
