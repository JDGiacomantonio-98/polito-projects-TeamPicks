import os
import secrets
from PIL import Image
from math import ceil
from random import random, randint
from flask import render_template, url_for, flash, redirect, request, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from teamgate import app, db, pswBurner, mail
from teamgate.forms import registrationForm_user, registrationForm_pub, loginForm, accountDashboardForm, resetRequestForm, resetPswForm, trialForm
from teamgate.dbModel import User, Pub


@app.route('/', methods=['GET', 'POST'])
def welcome():
    form = trialForm()
    if request.method == 'POST':
        # query number of pubs
        pubs = Pub.query.filter_by(city=form.city.data).count()
        return render_template('landingPage.html', city=form.city.data, pubs=pubs)
    elif current_user.is_authenticated:
        return render_template('homePage.html')
    else:
        return render_template('landingPage.html', form=form)


@app.route('/pricing')
def showPricing():
    return render_template('pricing.html', title='Pricing')


@app.route('/<userType>/<accType>/signup', methods=['GET', 'POST'])
def registration(userType, accType):
    if current_user.is_authenticated:
        return render_template('homePage.html')
    if userType == 'user':
        form = registrationForm_user()
    else:
        form = registrationForm_pub()
        form.subsType.data = accType   # used to auto-fill account type
    if request.method == 'GET':
        return render_template('signUp.html', title='Registration page', form=form, userType=userType)
    else:
        if form.validate_on_submit():
            pswHash = pswBurner.generate_password_hash(form.psw.data).decode('utf-8')
            if userType == 'user':
                newItem = User(
                    username=form.username.data,
                    firstName=form.firstName.data,
                    lastName=form.lastName.data,
                    city=form.city.data,
                    sex=form.sex.data,
                    email=form.emailAddr.data,
                    pswHash=pswHash
                )
                if newItem.sex != 'other':
                    newItem.img = str('default_' + newItem.sex + '_' + str(ceil(randint(1, 10) * random())) + '.jpg')
                else:
                    newItem.img = 'favicon.png'
            else:
                newItem = Pub(
                    username=form.username.data,
                    city=form.city.data,
                    businessAddress=form.businessAddress.data,
                    ownerFirstName=form.ownerFirstName.data,
                    ownerLastName=form.ownerLastName.data,
                    seatsMax=form.seatsMax.data,
                    subsType=form.subsType.data,
                    businessDescription=form.businessDescription.data,
                    email=form.emailAddr.data,
                    pswHash=pswHash
                )
                if newItem.subsType == 'free-acc':
                    newItem.isBookable = False
                else:
                    newItem.isBookable = True
            db.session.add(newItem)
            db.session.commit()
            newItem.send_ConfirmationEmail()
            session.clear()
            flash("Hi {}, your profile has been successfully created but is not yet active.".format(form.username.data),
                  'success')
            flash('A confirmation email has been sent to you. Open your inbox!', 'warning')
            return redirect(url_for('login'))
        elif form.username.data or form.businessName.data:
            flash("Something went wrong with your input, please check again.", 'danger')
            return render_template('signUp.html', title='Registration page', form=form, userType=userType)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('homePage.html')
    form = loginForm()
    if request.method == 'GET':
        return render_template('login.html', title='Login page', form=form)
    else:
        if form.validate_on_submit():
            query = User.query.filter_by(email=form.credential.data).first()
            endPoint = 'user'
            if not query:
                query = User.query.filter_by(username=form.credential.data).first()
                endPoint = 'user'
            if not query:
                query = Pub.query.filter_by(email=form.credential.data).first()
                endPoint = 'pub'
            if not query:
                query = Pub.query.filter_by(username=form.credential.data).first()
                endPoint = 'pub'
            session['dbModelType'] = endPoint
            if query and pswBurner.check_password_hash(query.pswHash, form.psw.data):
                session.permanent = True
                login_user(query, remember=form.rememberMe.data)
                flash("Hi {}, welcome back!".format(query.username), 'success')
                nextPage = request.args.get('next')
                if nextPage:
                    return redirect(nextPage)
                else:
                    return redirect(url_for('welcome'))
            elif query:
                flash('Login error : Invalid email or password.', 'danger')
                return render_template('login.html', title='Login page', form=form)
            else:
                flash("The provided credential are not linked to any existing account. Please try something else.", 'secondary')
                return render_template('login.html', title='Login page', form=form)
        return render_template('login.html', title='Login page', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You are now log out from the Gate. We hope to see you soon again!','secondary')
    return redirect(url_for('welcome'))


@app.route('/confirm-account/<token>')
@login_required
def confirmAccount(token):
    if current_user.confirmed:
        flash('You account has already been activated.', 'secondary')
        return redirect(url_for('welcome'))
    if current_user.confirmAccount(token):
        flash('Account confirmed successfully. Great, you are good to go now!', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'danger')
    return redirect(url_for('welcome'))


@login_required
@app.route('/delete-account')
def deleteAccount():
    if current_user:
        db.session.delete(current_user)
        db.session.commit()
        flash('Your account has been successfully removed. We are sad about that :C', 'secondary')
        return redirect(url_for('welcome'))


@app.route('/profile/<userInfo>/dashboard', methods=['GET', 'POST'])
@login_required
def showProfile(userInfo):
    form = accountDashboardForm()
    if 'user' == session.get('dbModelType'):
        if ('default_' in current_user.img) or (current_user.img == 'favicon.png'):
            imgFile = url_for('static', filename='profile_pics/AVATAR/' + current_user.img)
        else:
            imgFile = url_for('static', filename='profile_pics/users/' + current_user.img)
    if request.method == 'GET':
        if 'user' == session.get('dbModelType'):
            form.firstName.data = current_user.firstName
            form.lastName.data = current_user.lastName
            form.username.data = current_user.username
            form.emailAddr.data = current_user.email
        else:
            return render_template('pricing.html')
    else:
        if form.validate_on_submit():
            if form.submit.data:
                current_user.firstName = form.firstName.data
                current_user.lastName = form.lastName.data
                if current_user.email != form.emailAddr.data:
                    current_user.confirmed = False
                    current_user.email = form.emailAddr.data
                    current_user.send_ConfirmationEmail()
                current_user.img = save_profilePic(form.img.data)
                current_user.username = form.username.data
                db.session.commit()
            return redirect(url_for('showProfile', userInfo=current_user.username))
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
    resizedImg.thumbnail((200, 200))

    return resizedImg


def sendEmail(user, templatePath, mailTitle, token=None):
    msg = Message('TeamGate Account -- ' + mailTitle.upper(),
                  sender='teamgate.help@gmail.com',
                  recipients=[user.email])
    if token:
        msg.body = render_template(templatePath + '.txt', token=token, user=user)
    else:
        msg.body = render_template(templatePath + '.txt', user=user)
    # _external parameter allow to generate an absolute URL whose works outside app environment
    mail.send(msg)


@app.route('/<callerRoute>/acc-confirmation')
@login_required
def sendConfirmation(callerRoute):
    current_user.send_ConfirmationEmail()
    if callerRoute == 'profile':
        return redirect(url_for('showProfile', userInfo=current_user.username))


@app.route('/reset-request', methods=['GET', 'POST'])
def send_resetRequest():
    if current_user.is_authenticated:
        flash('You are logged in already.', 'info')
        return redirect(url_for('welcome'))
    form = resetRequestForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # send user an email
            user = User.query.filter_by(email=form.emailAddr.data).first()
            sendEmail(user, 'email-copy/reset-psw', 'psw reset', token=user.createToken())
            flash('An email has been sent to your inbox containing all instructions to reset your password!', 'warning')
            return redirect(url_for('login'))
    return render_template('resetRequest.html', title='Reset your psw', form=form)


@app.route('/pswReset/<token>', methods=['GET', 'POST'])
def pswReset(token):
    if current_user.is_authenticated:
        flash('You are logged in already.', 'info')
        return redirect(url_for('welcome'))
    user = User.verifyToken_pswReset(token)
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
                return redirect(url_for('showProfile', userInfo=current_user.username))
    return render_template('resetPsw.html', title='Resetting your psw', form=form)


@app.route('/contacts')
def contact():
    return render_template('contactUs.html', title='Let Us Know!', heading='We are glad to hear from you.')


@app.route('/find-a-pub')
def findPub():
    return render_template('findPub.html')


@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500


@app.route('/<callerPage>/work-in-progress')
def show_wip(callerPage):
    return render_template('errors/wip.html')


@app.route('/HTMLHelp')
def openVocabulary():
    return render_template('html-vocabulary.html')
