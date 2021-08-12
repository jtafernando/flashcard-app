# This blueprint stores all routes (urls) related to user auth
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .user import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])  # allows this route to accept get and post requests
def login():
    if  request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Query User db table for user with matching email
        # this var represents a db entry from User db table
        user = User.query.filter_by(email=email).first()  

        if user:  # if user exists
            if check_password_hash(user.password, password):  # checks db user password against password entered in login page
                flash(f'Welcom back, {user.first_name}. Let\'s study!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='warning')
        else:
            flash('Email not found.', category='warning')
            
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])  # allows this route to accept get and post requests
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName') 
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email=email).first()

        if user:
            # user already exists therefore flash warning
            flash('Email already exists.', category='warning')
        elif len(email) < 4: 
            # flash warning message to user
            flash('Email must be at least 4 characters.', category='warning')
        elif len(first_name) < 1:
            flash('First name must be at least 1 character.', category='warning')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='warning')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)  # add user to database
            db.session.commit()  # update database
            flash(f'Account created. Welcome, {new_user.first_name}!', category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)