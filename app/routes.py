from flask import request
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, CreatePostForm
from app.models import User, Post

@app.route('/')
@app.route('/index')
@login_required
def index():

    posts = Post.query.all()

    return render_template(
        'index.html',
        title='Home',
        posts=posts,
    )

@app.route('/login', methods=['GET', "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():

        # Check if username submitted via form really exists in the DB
        user = User.query.filter_by(username=form.username.data).first()

        # If user is non-existent or password given is invalid,
        # redirect user to login page again
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))

        # Login user using credentials if it passes security
        login_user(user, remember = form.remember_me.data)

        next_page = request.args.get('next')

        # Security measure to avoid the 'next' argument to have values
        # outside the website
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        flash(f"Welcome user {form.username.data}!{' This computer will remember your credentials' if form.remember_me.data else ''}")

        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"Congratulations {user.username}, you are now a registered user!", "message")
        return redirect(url_for('login'))

    return render_template('register.html', title="Sign Up", form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.all()

    return render_template('user.html', user=user, posts=posts)

@app.route('/create_post', methods=['POST', 'GET'])
@login_required
def create_post():

    form = CreatePostForm()

    if form.validate_on_submit():

        new_post = Post(body=form.body.data, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()

        flash("Good job creating your new post!")
        return redirect(url_for('index'))

    return render_template('create_post.html', title='New Post', form = form)
