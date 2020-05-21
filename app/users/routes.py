from flask import render_template, url_for, flash, redirect, request, session, abort
from flask_login import login_user, logout_user, login_required, current_user

from app.users.methods import save_profilePic, hash_psw, verify_psw, verify_token, confirm_account
from app.users.forms import RegistrationForm_base, RegistrationForm_pub, LoginForm, ProfileDashboardForm, ResetPswForm, CreateGroupForm, ResetRequestForm, SearchItemsForm
from app.users import users
from app.main.methods import send_confirmation_email, send_pswReset_email
from app import db
from app.dbModels import User, Owner, Group

# following routes are user-specific no need for 'app' instance


@users.route('/<userType>/<accType>/signup', methods=['GET', 'POST'])
def registration(userType, accType):
    if current_user.is_authenticated and current_user.confirmed:
        return render_template('home.html')
    if userType == 'user':
        form = RegistrationForm_base()
    else:
        form = RegistrationForm_pub()
        form.subsType.data = accType   # used to auto-fill account type
    if request.method == 'GET':
        return render_template('sign_up.html', title='Registration page', form=form, userType=userType)
    else:
        if form.validate_on_submit():
            if userType == 'user':
                newItem = User(
                    username=form.username.data,
                    firstName=form.firstName.data,
                    lastName=form.lastName.data,
                    city=form.city.data,
                    sex=form.sex.data,
                    email=form.email.data,
                    pswHash=hash_psw(form.confirmPsw.data)
                )
                newItem.img = newItem.set_defaultImg()
            else:
                newItem = Owner(
                    subsType=form.subsType.data,
                    city=form.city.data,
                    username=form.username.data,
                    firstName=form.ownerFirstName.data,
                    lastName=form.ownerLastName.data,
                    email=form.email.data,
                    pswHash=hash_psw(form.confirmPsw.data)
                )
                if newItem.subsType == 'free-acc':
                    newItem.isBookable = False
                else:
                    newItem.isBookable = True
            db.session.add(newItem)
            db.session.commit()
            send_confirmation_email(recipient=newItem)
            session.clear()
            flash("Hi {}, your profile has been successfully created but is not yet active.".format(form.username.data),
                  'success')
            flash('A confirmation email has been sent to you. Open your inbox!', 'warning')
            return redirect(url_for('users.login'))
        elif form.username.data or form.businessName.data:
            flash("Something went wrong with your input, please check again.", 'danger')
            return render_template('sign_up.html', title='Registration page', form=form, userType=userType)


@users.route('/confirm-account/<token>')
def activate(token):
    # if user comes from email confirmation link there is no current user to check
    if (not current_user.is_anonymous) and current_user.confirmed:
        flash('You account has already been activated.', 'secondary')
        return redirect(url_for('users.home', username=current_user.username))
    user = confirm_account(token)
    if user:
        flash('Account confirmed successfully. Great, you are good to go now!', 'success')
        login_user(user, remember=False)
        return redirect(url_for('users.home', username=user.username))
    else:
        flash('The confirmation link is invalid or has expired.', 'danger')
    return redirect(url_for('main.index'))


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.confirmed:
        return redirect(url_for('main.index'))
    form = LoginForm()
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
                query = Owner.query.filter_by(email=form.credential.data).first()
                endPoint = 'pub'
            if not query:
                query = Owner.query.filter_by(username=form.credential.data).first()
                endPoint = 'pub'
            session['dbModelType'] = endPoint
            if query and verify_psw(query.pswHash, form.psw.data):
                login_user(query, remember=form.rememberMe.data)
                if current_user.confirmed:
                    flash("Hi {}, welcome back!".format(query.username), 'success')
                    nextPage = request.args.get('next')
                    if nextPage:
                        return redirect(nextPage)
                    else:
                        return redirect(url_for('main.index'))
                else:
                    send_confirmation_email(recipient=current_user)
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


@users.route('/<username>/homepage', methods=['GET', 'POST'])
def home(username):
    form = SearchItemsForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            return render_template('search_results.html')
        return redirect(url_for('users.home', usermame=current_user.username))
    return render_template('home.html', form=form)


@users.route('/<username>/create-your-group', methods=['GET', 'POST'])
@login_required
def create_group(username):
    form = CreateGroupForm()
    if request.method == 'GET':
        return render_template('create_group.html', form=form, title='create your group')
    if form.validate_on_submit():
        if current_user.has_permission_to('CREATE-GROUP'):
            itm = Group(name=form.name.data)
    else:
        return redirect(url_for('users.create_group', username=current_user.username))


@users.route('/<username>/profile-dashboard', methods=['GET', 'POST'])
@login_required
def open_profile(username):
    form = ProfileDashboardForm()
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
        # update profile info if dashboard inputs are valid
        if form.validate_on_submit():
            if form.submit.data:
                current_user.firstName = form.firstName.data
                current_user.lastName = form.lastName.data
                if current_user.email != form.emailAddr.data:
                    current_user.confirmed = False
                    current_user.email = form.emailAddr.data
                    send_confirmation_email(recipient=current_user, flash_msg=True)
                current_user.img = save_profilePic(form.img.data)
                current_user.username = form.username.data
                db.session.commit()
            if form.delete.data:
                session['del'] = True
            else:
                session['del'] = False
            flash('You profile has been updated!', 'success')
            return redirect(url_for('users.open_profile', userInfo=current_user.username))
        flash('There are some problem with your input: please make correction before resubmitting !', 'danger')
    return render_template('profile.html', title='{} {}'.format(current_user.firstName, current_user.lastName), imgFile=current_user.get_imgFile(), form=form)


@users.route('/<ID>/delete-account')
@login_required
def delete_account(ID):
    # deletion should be authorized only by code and not by manual writing the URL
    if int(ID) == current_user.id and session['del']:  # error here
        db.session.delete(current_user)
        db.session.commit()
        flash('Your account has been successfully removed. We are sad about that :C', 'secondary')
        return redirect(url_for('main.index'))
    abort(403)


@users.route('/reset-request', methods=['GET', 'POST'])
def send_resetRequest():
    if current_user.is_authenticated and current_user.confirmed:
        flash('You are logged in already.', 'info')
        return redirect(url_for('main.index'))
    form = ResetRequestForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # send user an email
            query = User.query.filter_by(email=form.emailAddr.data).first()
            if not query:
                query = Owner.query.filter_by(email=form.emailAddr.data).first()
            if query.confirmed:
                send_pswReset_email(recipient=query)
                flash('An email has been sent to your inbox containing all instructions to reset your password!', 'warning')
                return redirect(url_for('users.login'))
            else:
                flash("Your account still require activation. Please check your email inbox.", 'warning')
                return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset your psw', form=form)


@users.route('/pswReset/<token>', methods=['GET', 'POST'])
def reset_psw(token):
    if current_user.is_authenticated:
        flash('You are logged in already.', 'info')
        return redirect(url_for('main.index'))
    user = verify_token(token)
    if not user:
        flash('The used token is expired or invalid.', 'danger')
        return redirect(url_for('users.send_resetRequest'))
    else:
        form = ResetPswForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                user.pswHash = hash_psw(form.psw.data)
                db.session.commit()
                flash("Hi {}, your password has been successfully reset. Welcome back on board!".format(user.username), 'success')
                flash('To assure security on your account we need you to login again.', 'secondary')
                return redirect(url_for('users.login'))
    return render_template('psw_reset.html', title='Resetting your psw', form=form)
