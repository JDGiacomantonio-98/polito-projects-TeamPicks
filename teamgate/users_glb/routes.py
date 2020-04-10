from math import ceil
from random import random, randint
from flask import render_template, url_for, flash, redirect, request, session, abort, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from teamgate import db, pswBurner
from teamgate.users_glb.forms import registrationForm_user, registrationForm_pub, loginForm, accountDashboardForm, resetPswForm
from teamgate.users_glb.methods import save_profilePic
from teamgate.dbModel import User, Pub

users = Blueprint('users', __name__)

# following routes are user-specific no need for 'app' instance


@users.route('/<userType>/<accType>/signup', methods=['GET', 'POST'])
def registration(userType, accType):
    if current_user.is_authenticated and current_user.confirmed:
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
            return redirect(url_for('users.login'))
        elif form.username.data or form.businessName.data:
            flash("Something went wrong with your input, please check again.", 'danger')
            return render_template('signUp.html', title='Registration page', form=form, userType=userType)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.confirmed:
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
                login_user(query, remember=form.rememberMe.data)
                if current_user.confirmed:
                    flash("Hi {}, welcome back!".format(query.username), 'success')
                    nextPage = request.args.get('next')
                    if nextPage:
                        return redirect(nextPage)
                    else:
                        return redirect(url_for('main.index'))
                else:
                    current_user.send_ConfirmationEmail()
                    flash("Your account still require activation. Please check your email inbox.", 'warning')
            elif query:
                flash('Login error : Invalid email or password.', 'danger')
                return render_template('login.html', title='Login page', form=form)
            else:
                flash("The provided credential are not linked to any existing account. Please try something else.", 'secondary')
                return render_template('login.html', title='Login page', form=form)
        return render_template('login.html', title='Login page', form=form)


@users.route('/logout')
def logout():
    logout_user()
    flash('You are now log out from the Gate. We hope to see you soon again!', 'secondary')
    return redirect(url_for('main.index'))


@users.route('/profile/<userInfo>/dashboard', methods=['GET', 'POST'])
@login_required
def showProfile(userInfo):
    form = accountDashboardForm()
    if 'user' == session.get('dbModelType'):
        if ('default_' in current_user.img) or (current_user.img == 'favicon.png'):
            imgFile = url_for('static', filename='profile_pics/AVATAR/' + current_user.img)
        else:
            imgFile = url_for('static', filename='profile_pics/users/' + current_user.img)
    if request.method == 'GET':
        if not current_user.confirmed:
            flash('Your profile has been temporally deactivated until you reconfirm it.', 'secondary')
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
                    current_user.send_ConfirmationEmail(flash_msg=True)
                current_user.img = save_profilePic(form.img.data)
                current_user.username = form.username.data
                db.session.commit()
            if form.delete.data:
                session['del'] = True
            else:
                session['del'] = False
            return redirect(url_for('main.showProfile', userInfo=current_user.username))
    return render_template('profilePage.html', title=current_user.firstName + " " + current_user.lastName, imgFile=imgFile, form=form)


@login_required
@users.route('/<ID>/delete-account')
def deleteAccount(ID):
    # deletion should be authorized only by code and not by manual writing the URL
    if int(ID) == current_user.id and session['del']:
        db.session.delete(current_user)
        db.session.commit()
        flash('Your account has been successfully removed. We are sad about that :C', 'secondary')
        return redirect(url_for('main.index'))
    abort(403)


@users.route('/pswReset/<token>', methods=['GET', 'POST'])
def pswReset(token):
    if current_user.is_authenticated:
        flash('You are logged in already.', 'info')
        return redirect(url_for('main.index'))
    user = User.verifyToken_pswReset(token)
    if not user:
        flash('The used token is expired or invalid.', 'danger')
        return redirect(url_for('main.send_resetRequest'))
    else:
        form = resetPswForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                pswHash = pswBurner.generate_password_hash(form.psw.data).decode('utf-8')
                user.pswHash = pswHash
                db.session.commit()
                login_user(user, remember=False)
                flash("Hi {}, your password has been successfully reset. Welcome back on board!".format(current_user.username), 'success')
                return redirect(url_for('users.showProfile', userInfo=current_user.username))
    return render_template('resetPsw.html', title='Resetting your psw', form=form)
