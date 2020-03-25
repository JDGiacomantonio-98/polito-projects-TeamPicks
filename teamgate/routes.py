import os
import secrets
from PIL import Image
from math import ceil
from random import random, randint
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from teamgate import app, db, pswBurner, mail
from teamgate.forms import registrationForm, loginForm, accountDashboardForm, resetRequestForm, resetPswForm, landingForm
from teamgate.dbModel import User


@app.route('/', methods=['GET', 'POST'])
def welcome():
    form = landingForm()
    return render_template('landingPage.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    form = registrationForm()
    if request.method == 'GET':
        return render_template('signUp.html', title='Registration page', form=form)
    else:
        if form.validate_on_submit():
            pswHash = pswBurner.generate_password_hash(form.psw.data).decode('utf-8')
            user = User(username=form.username.data,
                        firstName=form.firstName.data,
                        lastName=form.lastName.data,
                        sex=form.sex.data,
                        email=form.emailAddr.data,
                        pswHash=pswHash)
            if user.sex != 'other':
                user.img = str('default_' + user.sex + '_' + str(ceil(randint(1, 10) * random())) + '.jpg')
            else:
                user.img = 'favicon.png'
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=False)
            flash("Hi {}, your profile has been successfully created. Welcome on board!".format(form.username.data), 'success')
            return redirect(url_for('openProfile', userInfo=form.username.data))
        if form.username.data:
            flash("Something went wrong with your input, please check again.", 'danger')
            return render_template('signUp.html', title='Registration page', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    form = loginForm()
    if request.method == 'GET':
        return render_template('login.html', title='Login page', form=form)
    else:
        if form.validate_on_submit():
            currentUser = User.query.filter_by(email=form.emailAddr.data).first()
            if currentUser and pswBurner.check_password_hash(currentUser.pswHash, form.psw.data):
                login_user(currentUser, remember=form.rememberMe.data)
                flash("Hi {}, welcome back!".format(currentUser.username), 'success')
                nextPage = request.args.get('next')
                if nextPage:
                    return redirect(nextPage)
                else:
                    return redirect(url_for('welcome'))
            elif currentUser:
                flash('Login error : Invalid email or password.', 'danger')
                return render_template('login.html', title='Login page', form=form)
            else:
                flash("The provided credential are not linked to any existing account. Please try something else.", 'secondary')
                return redirect(url_for('login'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('welcome'))


@app.route('/profile/<userInfo>/dashboard', methods=['GET', 'POST'])
@login_required
def openProfile(userInfo):
    if ('default_' in current_user.img) or (current_user.img == 'favicon.png'):
        imgFile = url_for('static', filename='profile_pics/AVATAR/' + current_user.img)
    else:
        imgFile = url_for('static', filename='profile_pics/users/' + current_user.img)
    form = accountDashboardForm()
    if request.method == 'GET':
        form.firstName.data = current_user.firstName
        form.lastName.data = current_user.lastName
        form.username.data = current_user.username
        form.emailAddr.data = current_user.email
    else:
        if form.validate_on_submit():
            current_user.firstName = form.firstName.data
            current_user.lastName = form.lastName.data
            current_user.email = form.emailAddr.data
            current_user.img = save_profilePic(form.img.data)
            current_user.username = form.username.data
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('openProfile', userInfo=current_user.username))
    return render_template('profilePage.html', title=current_user.firstName + " " + current_user.lastName, imgFile=imgFile, form=form)


def save_profilePic(imgFile):
    if imgFile:
        hexCode = secrets.token_hex(6)
        while hexCode in current_user.img:
            hexCode = secrets.token_hex(6)
        if ('default_' not in current_user.img) and (current_user.img != 'favicon.png'):
            sourcePath = os.path.join(app.root_path, 'static/profile_pics/users', current_user.img)
            os.remove(sourcePath)
        fileName, fileExt = os.path.splitext(imgFile.filename)
        fileName = hexCode + fileExt.lower()
        targetPath = os.path.join(app.root_path, 'static/profile_pics/users', fileName)
        imgFile = resizeTo125(imgFile)
        imgFile.save(targetPath)
    else:
        fileName = current_user.img
    return fileName


def resizeTo125(imgFile):
    resizedImg = Image.open(imgFile)
    resizedImg.thumbnail((125, 125))

    return resizedImg


def send_resetEmail(user):
    token = user.create_ResetToken()
    msg = Message('TeamGate Account -- PASSWORD RESET',
                  sender='teamgate.help@gmail.com',
                  recipients=[user.email])
    msg.body = 'Hi, you received this email because our server received a password reset request.' \
               'password\n\nClick on the following link to reset your password :\n\n{}\n\n' \
               'If you not recognize this request please ignore it and remove this ' \
               'email from your inbox. In this way, no changes will be applied to your profile.'.format(url_for('pswReset', token=token, _external=True))
    # _external parameter allow to generate an absolute URL whose works outside app environment
    mail.send(msg)


@app.route('/reset-request', methods=['GET', 'POST'])
def send_resetRequest():
    if current_user.is_authenticated:
        flash('You are logged in already.', 'info')
        return redirect(url_for('welcome'))
    form = resetRequestForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # send user an email
            send_resetEmail(User.query.filter_by(email=form.emailAddr.data).first())
            flash('An email has been sent to your inbox containing all instructions to reset your psw!', 'secondary')
            return redirect(url_for('login'))
    return render_template('resetRequest.html', title='Reset your psw', form=form)


@app.route('/pswReset/<token>', methods=['GET', 'POST'])
def pswReset(token):
    if current_user.is_authenticated:
        flash('You are logged in already.', 'info')
        return redirect(url_for('welcome'))
    user = User.verify_ResetToken(token)
    if not user:
        flash('The used token is expired or invalid.', 'danger')
        return redirect(url_for('send_resetRequest'))
    else:
        form = resetPswForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                pswHash = pswBurner.generate_password_hash(form.psw.data).decode('utf-8')
                user.pswHash = pswHash
                db.session.commit()
                login_user(user, remember=False)
                flash("Hi {}, your password has been successfully reset. Welcome back on board!".format(current_user.username), 'success')
                return redirect(url_for('openProfile', userInfo=current_user.username))
    return render_template('resetPsw.html', title='Resetting your psw', form=form)


@app.route('/contacts')
def contact():
    return render_template('contactUs.html', title='Let Us Know!', heading='We are glad to hear from you.')


@app.route('/HTMLHelp')
def openVocabulary():
    return render_template('html-vocabulary.html')
