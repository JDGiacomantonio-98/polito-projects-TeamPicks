from shutil import rmtree
from string import capwords

from flask import render_template, url_for, flash, redirect, request, abort, make_response, session, g
from flask_login import logout_user, login_required, current_user

from app.users.methods import upload_profilePic, upload_carousel
from app.auth.methods import lock_account
from app.users.forms import ProfileDashboardForm, UploadProfileImgForm, CreateGroupForm, SearchItemsForm, DeleteAccountForm, UploadProfileCarouselForm, CreatePubForm,SendBookingRequestForm
from app.users import users
from app.main.methods import send_confirmation_email, handle_userBin
from app import db
from app.dbModels import User, Owner, Group, Pub, Reservation


@users.before_app_request
def time_tracking():
	if not current_user.is_anonymous:
		current_user.set_last_active()
		db.session.add(current_user)
		db.session.commit()


@users.route('/<username>/homepage', methods=['GET', 'POST'])
@login_required
def home(username):
	if current_user.username != username:
		return redirect(url_for('users.home', username=current_user.username))
	form = SearchItemsForm()
	def_pubs = []
	for p in Pub.query.filter(Pub.owner.has(city=current_user.city)).all():
		if p.bookable:
			def_pubs.append(p)
	if request.method == 'POST':
		if form.validate_on_submit():
			if session['pull_from'] == 'user':
				u = User.query.filter_by(username=form.searchedItem.data).first()
				if u is None:
					return render_template('home.html', form=form, title='home', def_pubs=def_pubs, u=u, pull_from=session['pull_from'])
				session['q'] = u.id # avoids redundant queries in the profile page
				return redirect(url_for('users.profile', username=u.username))
			u = Owner.query.filter_by(username=form.searchedItem.data).first()
			if u is None:
				return render_template('home.html', form=form, title='home', def_pubs=def_pubs, u=u, pull_from=session['pull_from'])
			session['q'] = u.id # avoids redundant queries in the profile page
			return redirect(url_for('users.profile', username=u.username))
		return redirect(url_for('users.home', username=current_user.username))
	return render_template('home.html', form=form, title='home', def_pubs=def_pubs, pull_from=session['pull_from'])


@users.route('/<username>/profile-dashboard', methods=['GET', 'POST'])
@login_required
def profile(username):
	if current_user.username == username:
		profile_u = current_user
		try:
			session.pop('q')
		except KeyError:
			pass
	else:
		try:
			if session['pull_from'] == 'user':
				profile_u = User.query.get(int(session['q']))
			else:
				profile_u = Owner.query.get(int(session['q']))
		except KeyError:
			if session['pull_from'] == 'user':
				profile_u = User.query.filter_by(username=username).first()
			else:
				profile_u = Owner.query.filter_by(username=username).first()
	if profile_u is None:
		flash('This user do not exist!', 'warning')
		return redirect(url_for('users.home', username=current_user.username))
	form_img = UploadProfileImgForm()
	form_carousel = UploadProfileCarouselForm()
	if current_user.id == profile_u.id:
		form_info = ProfileDashboardForm()
		if request.method == 'POST':
			if form_img.upload_img.data:
				if form_img.validate():
					current_user.profile_img = upload_profilePic(form_img.img.data)
					db.session.commit()
					flash('You profile has been updated!', 'success')
					return redirect(url_for('users.profile', username=current_user.username))
				flash('There are some problem with your input: please make correction before resubmitting !', 'danger')
				return render_template('profile.html', pull_from=session['pull_from'], title=f'{current_user.firstName} {current_user.lastName}',
									   is_viewer=(current_user.id != profile_u.id), user=current_user, imgFile=current_user.get_imgFile(),
									   carousel=current_user.get_imgCarousel(), groups=current_user.groups.count(), form_info=form_info, form_img=form_img)
			if form_img.modify_about_me.data:
				if form_img.validate():
					current_user.about_me = form_img.about_me.data
					if session['pull_from'] != 'user':
						current_user.pub.description = current_user.about_me
					db.session.commit()
					flash('You profile has been updated!', 'success')
					return redirect(url_for('users.profile', username=current_user.username))
				flash('There are some problem with your input: please make correction before resubmitting !', 'danger')
				return render_template('profile.html', pull_from=session['pull_from'], title=f'{current_user.firstName} {current_user.lastName}',
									   is_viewer=(current_user.id != profile_u.id), user=current_user, imgFile=current_user.get_imgFile(),
									   carousel=current_user.get_imgCarousel(), groups=current_user.groups.count(), form_info=form_info, form_img=form_img)
			# if something has been changed in the dashboard
			if form_info.submit.data:
				if form_info.validate():
					if current_user.email != form_info.email.data:
						current_user.confirmed = False
						current_user.email = form_info.email.data
						send_confirmation_email(recipient=current_user, email_update=True, flash_msg=True)
					current_user.firstName = form_info.firstName.data
					current_user.lastName = form_info.lastName.data
					current_user.username = form_info.username.data
					db.session.commit()
					flash('You profile has been updated!', 'success')
					return redirect(url_for('users.profile', username=current_user.username))
				flash('There are some problem with your input: please make correction before resubmitting !', 'danger')
				form_img.about_me.data = current_user.about_me
				return render_template('profile.html', pull_from=session['pull_from'], title=f'{current_user.firstName} {current_user.lastName}',
									   is_viewer=(current_user.id != profile_u.id), user=profile_u, imgFile=profile_u.get_imgFile(),
									   carousel=profile_u.get_imgCarousel(), form_info=form_info, form_img=form_img, form_carousel=form_carousel, groups=profile_u.groups.count())
			if form_carousel.upload_carousel.data:
				if form_carousel.validate():
					upload_carousel(form_carousel.images.data)
					flash('You profile has been updated!', 'success')
					return redirect(url_for('users.profile', username=current_user.username))
		form_info.firstName.data = capwords(current_user.firstName)
		form_info.lastName.data = capwords(current_user.lastName)
		form_info.username.data = current_user.username
		form_info.email.data = current_user.email
		if current_user.about_me:
			form_img.about_me.data = current_user.about_me.capitalize()
		else:
			form_img.about_me.data = ''
		if session['pull_from'] == 'user':
			resp = make_response(render_template('profile.html', pull_from=session['pull_from'], title=f'{current_user.firstName} {current_user.lastName}',
											 	is_viewer=(current_user.id != profile_u.id), user=current_user, imgFile=current_user.get_imgFile(),
											 	carousel=current_user.get_imgCarousel(), reservations=current_user.reservations.count(), groups=current_user.groups.count(),
												form_info=form_info, form_img=form_img, form_carousel=form_carousel))
		elif current_user.pub:
			resp = make_response(render_template('profile.html', pull_from=session['pull_from'], title=f'{current_user.firstName} {current_user.lastName}',
												is_viewer=(current_user.id != profile_u.id), user=current_user, imgFile=current_user.get_imgFile(),
												carousel=current_user.get_imgCarousel(), reservations=current_user.pub.reservations.count(),
												form_info=form_info, form_img=form_img, form_carousel=form_carousel))
		else:
			resp = make_response(render_template('profile.html', pull_from=session['pull_from'], title=f'{current_user.firstName} {current_user.lastName}',
												is_viewer=(current_user.id != profile_u.id), user=current_user, imgFile=current_user.get_imgFile(),
												carousel=current_user.get_imgCarousel(),
												form_info=form_info, form_img=form_img, form_carousel=form_carousel))
		resp.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
		resp.headers['Cache-Control'] = 'public, max-age=0'
		return resp
	if current_user.confirmed:
		if profile_u.about_me:
			form_img.about_me.data = profile_u.about_me.capitalize()
		else:
			form_img.about_me.data = ''
		if session['pull_from'] == 'user':
			return render_template('profile.html', pull_from=session['pull_from'], title=f'{profile_u.firstName} {profile_u.lastName}',
								   is_viewer=(current_user.id != profile_u.id), user=profile_u, imgFile=profile_u.get_imgFile(),
								   carousel=profile_u.get_imgCarousel(), form_img=form_img, form_carousel=form_carousel, groups=profile_u.groups.count())
		return render_template('profile.html', pull_from=session['pull_from'], title=f'{profile_u.firstName} {profile_u.lastName}',
							   is_viewer=(current_user.id != profile_u.id), user=profile_u, imgFile=profile_u.get_imgFile(),
							   carousel=profile_u.get_imgCarousel(), form_img=form_img, form_carousel=form_carousel)
	flash('Your profile require an email confirmation to browse TeamPicks.', 'secondary')
	return redirect(url_for('users.profile', username=current_user.username))


@users.route('/delete/<u_id>', methods=['GET', 'POST'])
@login_required
def delete_account(u_id, ATTEMPTS=10):
	if int(u_id) == current_user.id: 	# deletion is authorized only by code and not by manual writing the URL
		if not current_user.is_acc_locked():
			form = DeleteAccountForm()
			if request.method == 'POST':
				session['del-attempt'] += 1
				if form.validate_on_submit():
					rmtree(handle_userBin(current_user.get_file_address(), absolute_url=True))
					db.session.delete(current_user)
					db.session.commit()
					logout_user()
					flash('Your account has been successfully removed. We are sad about that :C', 'secondary')
					session.clear()
					return redirect(url_for('main.index'))
				if ATTEMPTS - session['del-attempt'] != 0:
					if ATTEMPTS - session['del-attempt'] <= 3:
						flash(f'{ATTEMPTS - session["del-attempt"]} attempts remaining', 'danger')
					return render_template('delete_account.html', form=form, title='are you sure about that?', pull_from=session['pull_from'])
				lock_account(current_user)
				logout_user()
				# notify teampicks staff by email
				flash('Your account has been temporarly locked because the system detected a brutal attempt to delete it.\nTeampicks has been notified about that.', 'danger')
				return redirect(url_for('main.index'))
			try:
				session['del-attempt']
			except KeyError:
				session['del-attempt'] = 0
			return render_template('delete_account.html', form=form, title=':C', pull_from=session['pull_from'])
		logout_user()
		return redirect(url_for('main.index'))
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
	return render_template('create_group.html', form=form, title='your new group', pull_from=session['pull_from'])


@users.route('/<username>/create-new-pub', methods=['GET', 'POST'])
@login_required
def create_pub(username):
	if session['pull_from'] == 'user':
		return redirect(url_for('users.home', username=current_user.username))
	if current_user.pub:
		flash('Your pub is already registred.', 'info')
		return redirect(url_for('users.home', username=current_user.username))
	form = CreatePubForm()
	if request.method == 'POST':
		p = Pub(name=form.name.data,
				address=form.address.data,
				phone_num=form.phone_num.data,
				seats_max=form.seats_max.data,
				description=form.description.data
				)
		db.session.add(p)
		current_user.associate_pub(p)
		db.session.commit()
	return render_template('create_pub.html', form=form, pull_from=session['pull_from'])


@users.route('/pub/<int:p_id>', methods=['GET', 'POST'])
@login_required
def visit_pub(p_id):
	p = Pub.query.get(p_id)
	if session['pull_from'] == 'user':
		carousel = p.owner.get_imgCarousel(foreign_session=True)
	else:
		carousel = p.owner.get_imgCarousel()
	grid = len(carousel)
	form = SendBookingRequestForm()
	if request.method == 'POST':
		if p.owner.id != current_user.id:
			if form.validate():
				pass
			current_user.send_bookingReq(pub=p, guests=form.guests.data)
			return render_template('pub_page.html', pub=p, carousel=carousel, grid=grid, pull_from=session['pull_from'], form=form)
		flash('Did you want to book from yourself ?', 'secondary')
		return redirect(url_for('users.visit_pub', p_id=p.id))
	form.guests.data = '2'
	return render_template('pub_page.html', pub=p, carousel=carousel, grid=grid, pull_from=session['pull_from'], form=form)


@users.route('/<username>/manage-reservation/all', methods=['GET', 'POST'])
@login_required
def manage_reservations(username):
	page = request.args.get('page', 1, type=int)
	if session['pull_from'] == 'user':
		pagination = current_user.reservations.filter_by(confirmed=False).order_by(Reservation.date.desc()).paginate(page, per_page=16, error_out=False)
	else:
		pagination = current_user.pub.reservations.filter_by(confirmed=False).order_by(Reservation.date.desc()).paginate(page, per_page=16, error_out=False)
	if request.method == 'POST':
		return
	return render_template('booking_manager.html', reservations=pagination.items, pagination=pagination, pull_from=session['pull_from'])


@users.route('/find-pubs', methods=['GET', 'POST'])
@login_required
def search_pub():
	form = SearchItemsForm()
	local_pubs = []
	for p in Pub.query.filter(Pub.owner.has(city=current_user.city)).all():
		if p.bookable:
			local_pubs.append(p)
	if request.method == 'POST':
		if form.searchedItem.data:
			p = Pub.query.filter_by(name=form.searchedItem.data).first()
			return render_template('search_pub.html', form=form, local_pubs=local_pubs, query_pub=p, pull_from=session['pull_from'])
		return redirect(url_for('users.search_pub'))
	return render_template('search_pub.html', form=form, local_pubs=local_pubs, pull_from=session['pull_from'])


@users.route('/follow/<int:u_id>')
@login_required
def follow(u_id):
	u = User.query.get(u_id)
	if not current_user.is_following(u):
		current_user.follow(u)
		flash(f'You are now following {u.username}', 'success')
	return redirect(url_for('users.profile', username=u.username))


@users.route('/unfollow/<int:u_id>')
@login_required
def unfollow(u_id):
	u = User.query.get(u_id)
	if current_user.is_following(u):
		current_user.unfollow(u)
		flash(f'You are not following {u.username} anymore.', 'danger')
	return redirect(url_for('users.profile', username=u.username))
