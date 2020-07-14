from flask import render_template, url_for, flash, redirect, request, session, make_response
from flask_login import login_user, logout_user, current_user

from app.auth.methods import hash_psw, verify_psw, verify_token, confirm_account, lock_account
from app.auth.forms import RegistrationForm_base, RegistrationForm_owner, LoginForm, ResetPswForm, ResetRequestForm
from app.auth import auth
from app.main.methods import send_confirmation_email, send_pswReset_email, find_user, cherryPick_user
from app import db
from app.dbModels import User, Owner


@auth.route('/<userType>/<accType>/signup', methods=['GET', 'POST'])
def registration(userType, accType):
	if current_user.is_authenticated and current_user.confirmed:
		return redirect(url_for('users.home', username=current_user.username))
	if userType == 'user':
		form = RegistrationForm_base()
	else:
		form = RegistrationForm_owner()
		form.subsType.data = accType   # used to auto-fill account type
	if request.method == 'POST':
		if form.validate_on_submit():
			if userType == 'user':
				newItem = User(
					username=form.username.data.lower(),
					firstName=form.firstName.data.lower(),
					lastName=form.lastName.data,
					city=form.city.data.lower(),
					sex=form.sex.data,
					email=form.email.data,
					hash=hash_psw(form.confirmPsw.data)
				)
			else:
				newItem = Owner(
					subsType=form.subsType.data,
					city=form.city.data.lower(),
					username=form.username.data,
					firstName=form.firstName.data.lower(),
					lastName=form.lastName.data.lower(),
					email=form.email.data,
					hash=hash_psw(form.confirmPsw.data)
				)
				newItem.evaluate_subs()
			db.session.add(newItem)
			db.session.commit()
			send_confirmation_email(recipient=newItem)
			login_user(newItem, remember=True)
			flash(f"Hi {form.username.data}, your profile has been successfully created but is not yet active.", 'success')
			flash('A confirmation email has been sent to you. Open your inbox!', 'warning')
			return redirect(url_for('auth.login'))
		elif form.username.data or form.businessName.data:
			flash("Something went wrong with your input, please check again.", 'danger')
			return render_template('register.html', title='Registration page', form=form, userType=userType)
	return render_template('register.html', title='Registration page', form=form, userType=userType)


@auth.route('/confirm-account/<token>_<email_update>')
def activate(token, email_update):
	# if user comes from email confirmation link there is no current user to check
	if (not current_user.is_anonymous) and current_user.confirmed:
		flash('You account has already been activated.', 'secondary')
		return redirect(url_for('users.home'))
	u = confirm_account(token)
	if u:
		flash('Account confirmed successfully. Great, you are good to go now!', 'success')
		if email_update:
			return redirect(url_for('users.profile', username=u.username))
		return redirect(url_for('users.home', username=u.username))
	flash('The confirmation link is invalid or has expired.', 'danger')
	return redirect(url_for('main.index'))


@auth.route('/login', methods=['GET', 'POST'])
def login(ATTEMPTS=5):
	if current_user.is_authenticated and current_user.confirmed:
		return redirect(url_for('users.home', username=current_user.username))
	form = LoginForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			try:
				if session['trace']:
					try:
						session['log-attempt']
					except KeyError:
						session['log-attempt'] = 0
					trace = session['trace'].split('%')
					if form.credential.data in (trace[1], trace[2]):
						query = cherryPick_user(pull_from=trace[0], u_id=trace[3])
					else:
						session.pop('trace')
						try:
							session.pop('log-attempt')
						except KeyError:
							session['log-attempt'] = 0
						query = find_user(form.credential.data)
				else:
					query = find_user(form.credential.data)
			except KeyError:
				query = find_user(form.credential.data)
			if query[0]:
				if query[0].is_acc_locked():
					return redirect(url_for('auth.login'))
				session['pull_from'] = query[1]
				if verify_psw(query[0].hash, form.psw.data):
					login_user(query[0], remember=form.rememberMe.data)
					if current_user.confirmed:
						flash(f"Hi {query[0].username}, welcome back!", 'success')
						nextPage = request.args.get('next')
						if nextPage:
							return redirect(nextPage)
						return redirect(url_for('main.index'))
					else:
						send_confirmation_email(recipient=current_user)
						flash("Your account still require activation. Please check your email inbox.", 'warning')
						return redirect(url_for('auth.login'))
				session['log-attempt'] += 1
				if ATTEMPTS - session['log-attempt'] != 0:
					if ATTEMPTS - session['log-attempt'] <= 3:
						flash(f'{ATTEMPTS - session["log-attempt"]} attempts remaining', 'danger')
					flash('Login error : Invalid email or password.', 'danger')
					session['trace'] = f'{query[1]}%{query[0].username}%{query[0].email}%{query[0].id}'
					return render_template('login.html', title='Login page', form=form)
				lock_account(query[0])
			flash("The provided credential are not linked to any existing account. Please try something else.", 'secondary')
			return render_template('login.html', title='Login page', form=form)
		return render_template('login.html', title='Login page', form=form)
	session.clear()
	return render_template('login.html', title='Login page', form=form)


@auth.route('/logout')
def logout():
	logout_user()
	flash('You are now out of the Gate. We hope to see you soon again!', 'secondary')
	return redirect(url_for('main.index'))


@auth.route('/reset-request', methods=['GET', 'POST'])
def send_resetRequest():
	if current_user.is_authenticated and current_user.confirmed:
		flash('You are logged in already.', 'info')
		return redirect(url_for('users.home'))
	form = ResetRequestForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			query = find_user(form.email.data, email_only=True)
			if query[0].confirmed:
				send_pswReset_email(recipient=query[0])
				flash('An email has been sent to your inbox containing all instructions to reset your password!', 'warning')
				return redirect(url_for('auth.login'))
			else:
				flash("Your account still require activation. Please check your email inbox.", 'warning')
				return redirect(url_for('auth.login'))
	return render_template('reset_request.html', title='password reset', form=form)


@auth.route('/pswReset/<token>', methods=['GET', 'POST'])
def reset_psw(token):
	if current_user.is_authenticated:
		flash('You are logged in already.', 'info')
		return redirect(url_for('users.home'))
	user = verify_token(token)
	if not user:
		flash('The used token is expired or invalid.', 'danger')
		return redirect(url_for('auth.send_resetRequest'))
	form = ResetPswForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			user.hash = hash_psw(form.psw.data)
			db.session.commit()
			flash(f"Hi {user.username}, your password has been successfully reset. Welcome back on board!", 'success')
			flash('To assure security on your account we need you to login again.', 'secondary')
			return redirect(url_for('auth.login'))
	return render_template('psw_reset.html', title='Resetting your psw', form=form)


