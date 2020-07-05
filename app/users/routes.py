from flask import render_template, url_for, flash, redirect, request, session, abort
from flask_login import login_user, logout_user, login_required, current_user

from app.users.methods import save_profilePic, hash_psw, verify_psw, verify_token, confirm_account
from app.users.forms import RegistrationForm_base, RegistrationForm_owner, LoginForm, ProfileDashboardForm, ResetPswForm, CreateGroupForm, ResetRequestForm, SearchItemsForm, DeleteAccountForm
from app.users import users
from app.main.methods import send_confirmation_email, send_pswReset_email
from app import db
from app.dbModels import User, Owner, Group


@users.route('/<userType>/<accType>/signup', methods=['GET', 'POST'])
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
					username=form.username.data,
					firstName=form.firstName.data,
					lastName=form.lastName.data,
					city=form.city.data,
					sex=form.sex.data,
					email=form.email.data,
					pswHash=hash_psw(form.confirmPsw.data)
				)
			else:
				newItem = Owner(
					subsType=form.subsType.data,
					city=form.city.data,
					username=form.username.data,
					firstName=form.firstName.data,
					lastName=form.lastName.data,
					email=form.email.data,
					pswHash=hash_psw(form.confirmPsw.data)
				)
				newItem.evaluate_subs()
			db.session.add(newItem)
			db.session.commit()
			send_confirmation_email(recipient=newItem)
			# session.clear()
			login_user(newItem, remember=True)
			flash(f"Hi {form.username.data}, your profile has been successfully created but is not yet active.", 'success')
			flash('A confirmation email has been sent to you. Open your inbox!', 'warning')
			return redirect(url_for('users.login'))
		elif form.username.data or form.businessName.data:
			flash("Something went wrong with your input, please check again.", 'danger')
			return render_template('sign_up.html', title='Registration page', form=form, userType=userType)
	return render_template('sign_up.html', title='Registration page', form=form, userType=userType)


@users.route('/confirm-account/<token>')
def activate(token):
	# if user comes from email confirmation link there is no current user to check
	if (not current_user.is_anonymous) and current_user.confirmed:
		flash('You account has already been activated.', 'secondary')
		return redirect(url_for('users.home'))
	u = confirm_account(token)
	if u:
		flash('Account confirmed successfully. Great, you are good to go now!', 'success')
		return redirect(url_for('users.home', username=u.username))
	flash('The confirmation link is invalid or has expired.', 'danger')
	return redirect(url_for('main.index'))


@users.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated and current_user.confirmed:
		return redirect(url_for('users.home', username=current_user.username))
	form = LoginForm()
	if request.method == 'POST':
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
					flash(f"Hi {query.username}, welcome back!", 'success')
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
	return render_template('login.html', title='Login page', form=form)


@users.route('/logout')
def logout():
	logout_user()
	flash('You are now out of the Gate. We hope to see you soon again!', 'secondary')
	return redirect(url_for('main.index'))


@users.route('/<username>/homepage', methods=['GET', 'POST'])
@login_required
def home(username):
	form = SearchItemsForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			return render_template('search_results.html')
		return redirect(url_for('users.home', usermame=current_user.username))
	return render_template('home.html', form=form, title='home')


@users.route('/<username>/profile-dashboard', methods=['GET', 'POST'])
@login_required
def open_profile(username):
	form = ProfileDashboardForm()
	if request.method == 'POST':
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
			flash('You profile has been updated!', 'success')
			return redirect(url_for('users.open_profile', username=current_user.username))
		flash('There are some problem with your input: please make correction before resubmitting !', 'danger')
		return render_template('profile.html', title=f'{current_user.firstName} {current_user.lastName}', imgFile=current_user.get_imgFile(), form=form)
	if current_user.confirmed:
		if 'user' == session.get('dbModelType'):
			form.firstName.data = current_user.firstName
			form.lastName.data = current_user.lastName
			form.username.data = current_user.username
			form.emailAddr.data = current_user.email
			return render_template('profile.html', title=f'{current_user.firstName} {current_user.lastName}', imgFile=current_user.get_imgFile(), form=form)
		else:
			return render_template('errors/wip.html', title='coming soon!')
	flash('Your profile has been temporally deactivated until you reconfirm it.', 'secondary')
	return render_template('profile.html', title=f'{current_user.firstName} {current_user.lastName}', imgFile=current_user.get_imgFile(), form=form)


@users.route('/delete/<u_id>', methods=['GET', 'POST'])
@login_required
def delete_account(u_id):
	# deletion should be authorized only by code and not by manual writing the URL
	if int(u_id) == current_user.id:
		form = DeleteAccountForm()
		if request.method == 'POST':
			if form.validate_on_submit():
				db.session.delete(current_user)
				db.session.commit()
				logout_user()
				flash('Your account has been successfully removed. We are sad about that :C', 'secondary')
				return redirect(url_for('main.index'))
		return render_template('remove_account.html', form=form, title=':C')
	abort(403)


@users.route('/<username>/create-your-group', methods=['GET', 'POST'])
@login_required
def create_group(username):
	form = CreateGroupForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			if current_user.has_permission_to('CREATE-GROUP'):
				itm = Group(name=form.name.data)
		else:
			return redirect(url_for('users.create_group', username=current_user.username))
	return render_template('create_group.html', form=form, title='your new group')


@users.route('/reset-request', methods=['GET', 'POST'])
def send_resetRequest():
	if current_user.is_authenticated and current_user.confirmed:
		flash('You are logged in already.', 'info')
		return redirect(url_for('users.home'))
	form = ResetRequestForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			query = User.query.filter_by(email=form.email.data).first()
			if not query:
				query = Owner.query.filter_by(email=form.email.data).first()
			if query.confirmed:
				send_pswReset_email(recipient=query)
				flash('An email has been sent to your inbox containing all instructions to reset your password!', 'warning')
				return redirect(url_for('users.login'))
			else:
				flash("Your account still require activation. Please check your email inbox.", 'warning')
				return redirect(url_for('users.login'))
	return render_template('reset_request.html', title='password reset', form=form)


@users.route('/pswReset/<token>', methods=['GET', 'POST'])
def reset_psw(token):
	if current_user.is_authenticated:
		flash('You are logged in already.', 'info')
		return redirect(url_for('users.home'))
	user = verify_token(token)
	if not user:
		flash('The used token is expired or invalid.', 'danger')
		return redirect(url_for('users.send_resetRequest'))
	form = ResetPswForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			user.pswHash = hash_psw(form.psw.data)
			db.session.commit()
			flash(f"Hi {user.username}, your password has been successfully reset. Welcome back on board!", 'success')
			flash('To assure security on your account we need you to login again.', 'secondary')
			return redirect(url_for('users.login'))
	return render_template('psw_reset.html', title='Resetting your psw', form=form)
