from shutil import rmtree
from string import capwords

from flask import render_template, url_for, flash, redirect, request, abort, make_response, session
from flask_login import logout_user, login_required, current_user

from app.users.methods import upload_profilePic, upload_carousel
from app.auth.methods import lock_account
from app.users.forms import ProfileDashboardForm, UploadProfileImgForm, CreateGroupForm, SearchItemsForm, DeleteAccountForm, UploadProfileCarouselForm, CreatePubForm, SendBookingRequestForm, UpdateBookingReqForm, ReviewPubForm, PubDashboardForm
from app.users import users
from app.main.methods import send_confirmation_email, handle_userBin
from app import db
from app.dbModels import User, Owner, Group, Pub, Reservation, Follow, Review


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
	form_search = SearchItemsForm()
	page = request.args.get('page', default=1, type=int)
	if session['pull_from'] == 'user':
		pub_paginate = Pub.query.filter(Pub.owner.has(city=current_user.city)).filter_by(bookable=True).paginate(page, per_page=3, error_out=False)
		# paginate users groups
		friend_groups = []
		friend_list = []
		for f_id in Follow.get_all_followed_id(current_user):
			g = Group.query.filter(Group.subs.any(member_id=f_id)).first()
			if g:
				friend_groups.append(g)
				friend_list.append(f_id)
		# group_paginate = Group.query.filter(Group.subs.any(member_id=Follow.get_all_followed_id(current_user))).paginate(page, per_page=3, error_out=False)
	else:
		if current_user.pub:
			form_pub_dashboard = PubDashboardForm()
			res_paginate = Reservation.query.filter_by(at_id=current_user.pub.id).filter_by(confirmed=False).filter_by(cancelled=False).order_by(Reservation.date.asc()).paginate(page, per_page=3, error_out=False)
	if request.method == 'POST':
		if session['pull_from'] == 'owner':
			if form_pub_dashboard.set.data:
				if form_pub_dashboard.validate():
					current_user.pub.set_manually_availability(form_pub_dashboard.current_availability.data)
					db.session.commit()
					flash(f'{current_user.pub.name} availability for today set to {current_user.pub.get_availability()}. MAX : {current_user.pub.seats_max}', 'success')
					return redirect(url_for('users.home', username=current_user.username))
				return render_template('home.html', form_search=form_search, title='home', carousel=current_user.get_imgCarousel(), form_pub_dashboard=form_pub_dashboard, res_paginate=res_paginate, reservations=res_paginate.items, pull_from=session['pull_from'])
		if form_search.validate_on_submit():
			if session['pull_from'] == 'user':
				u = User.query.filter_by(username=form_search.searchedItem.data).first()
				if u is None:
					return render_template('home.html', form_search=form_search, title='home', pub_paginate=pub_paginate, pubs=pub_paginate.items, u=u, pull_from=session['pull_from'])
				session['q'] = u.id # avoids redundant queries in the profile page
				return redirect(url_for('users.profile', username=u.username))
			u = Owner.query.filter_by(username=form_search.searchedItem.data).first()
			if u is None:
				return render_template('home.html', form_search=form_search, title='home', carousel=current_user.get_imgCarousel(), form_pub_dashboard=form_pub_dashboard, res_paginate=res_paginate, reservations=res_paginate.items, u=u, pull_from=session['pull_from'])
			session['q'] = u.id # avoids redundant queries in the profile page
			return redirect(url_for('users.profile', username=u.username))
		return redirect(url_for('users.home', username=current_user.username))
	if session['pull_from'] == 'user':
		return render_template('home.html', form_search=form_search, title='home', friend_list=friend_list, friend_groups=friend_groups, pub_paginate=pub_paginate, pubs=pub_paginate.items, pull_from=session['pull_from'])
	if current_user.pub:
		form_pub_dashboard.current_availability.data = current_user.pub.get_availability()
		return render_template('home.html', form_search=form_search, form_pub_dashboard=form_pub_dashboard, title='home', carousel=current_user.get_imgCarousel(), res_paginate=res_paginate, reservations=res_paginate.items)
	return render_template('home.html', form_search=form_search, title='home')


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
						send_confirmation_email(recipient=current_user, pull_from=session['pull_from'], email_update=True, flash_msg=True)
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
			try:
				if form_carousel.upload_carousel.data:
					if form_carousel.validate():
						upload_carousel(form_carousel.images.data)
						flash('You profile has been updated!', 'success')
						return redirect(url_for('users.profile', username=current_user.username))
			except BaseException: # no file selected but form submitted
				flash("Choose some images from your device first before clicking upload.", 'warning')
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
											 	carousel=current_user.get_imgCarousel(), reservations=current_user.reservations.filter_by(cancelled=False).filter_by(confirmed=False).count(), groups=current_user.groups.count(),
												form_info=form_info, form_img=form_img, form_carousel=form_carousel))
		elif current_user.pub:
			resp = make_response(render_template('profile.html', pull_from=session['pull_from'], title=f'{current_user.firstName} {current_user.lastName}',
												is_viewer=(current_user.id != profile_u.id), user=current_user, imgFile=current_user.get_imgFile(),
												carousel=current_user.get_imgCarousel(), reservations=current_user.pub.reservations.filter_by(cancelled=False).filter_by(confirmed=False).count(),
												form_info=form_info, form_img=form_img, form_carousel=form_carousel))
		else:
			resp = make_response(render_template('profile.html', pull_from=session['pull_from'], title=f'{current_user.firstName} {current_user.lastName}',
												is_viewer=(current_user.id != profile_u.id), user=current_user, imgFile=current_user.get_imgFile(),
												carousel=current_user.get_imgCarousel(), form_info=form_info, form_img=form_img, form_carousel=form_carousel))
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
def delete_account(u_id, ATTEMPTS=8):
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
					session.clear()
					flash('Your account has been successfully removed. We are sad about that :C', 'secondary')
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


@users.route('/follow/<int:u_id>')
@login_required
def follow(u_id):
	u = User.query.get(u_id)
	if not current_user.is_following(u):
		current_user.follow(u)
		db.session.commit()
		flash(f'You are now following {u.username}', 'success')
	return redirect(url_for('users.profile', username=u.username))


@users.route('/unfollow/<int:u_id>')
@login_required
def unfollow(u_id):
	u = User.query.get(u_id)
	if current_user.is_following(u):
		current_user.unfollow(u)
		db.session.commit()
		flash(f'You are not following {u.username} anymore.', 'danger')
	return redirect(url_for('users.profile', username=u.username))


@users.route('/<username>/followers', methods=['GET', 'POST'])
@login_required
def show_followers(username):
	followers = []
	for f_id in Follow.get_all_following_id(User.query.filter_by(username=username).first()):
		followers.append(User.query.get(f_id))
	return render_template('friend_list.html', list=followers)


@users.route('/<username>/following', methods=['GET', 'POST'])
@login_required
def show_following(username):
	following = []
	for f_id in Follow.get_all_followed_id(User.query.filter_by(username=username).first()):
		following.append(User.query.get(f_id))
	return render_template('friend_list.html', list=following)


@users.route('/<username>/create-your-group', methods=['GET', 'POST'])
@login_required
def create_group(username):
	form = CreateGroupForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			if current_user.has_permission_to('CREATE-GROUP'):
				g = Group(name=form.name.data)
				db.session.add(g)
				current_user.join_as_admin(g)
				db.session.commit()
				return redirect(url_for('users.home', username=current_user.username))
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


@users.route('/find-pubs', methods=['GET', 'POST'])
@login_required
def search_pub():
	form = SearchItemsForm()
	page = request.args.get('page', default=1, type=int)
	paginate = Pub.query.filter(Pub.owner.has(city=current_user.city)).paginate(page, per_page=4, error_out=False)
	if request.method == 'POST':
		if form.searchedItem.data:
			p = Pub.query.filter_by(name=form.searchedItem.data).first()
			paginate = Pub.query.filter(Pub.owner.has(city=current_user.city)).paginate(page, per_page=3, error_out=False)
			return render_template('search_pub.html', form=form, paginate=paginate, local_pubs=paginate.items, query_pub=p, pull_from=session['pull_from'])
		return redirect(url_for('users.search_pub'))
	return render_template('search_pub.html', form=form, paginate=paginate, local_pubs=paginate.items, pull_from=session['pull_from'])


@users.route('/pub/<int:p_id>', methods=['GET', 'POST'])
@login_required
def visit_pub(p_id):
	p = Pub.query.get(p_id)
	if session['pull_from'] == 'user':
		carousel = p.owner.get_imgCarousel(foreign_session=True)
		form_review = ReviewPubForm()
	else:
		carousel = p.owner.get_imgCarousel()
	grid = len(carousel)
	form_booking = SendBookingRequestForm()
	page = request.args.get('page', 1, type=int)
	paginate_rev = p.reviews.paginate(page, per_page=6, error_out=False)
	if request.method == 'POST':
		if form_review.send_review.data:
			if form_review.validate():
				pass
			db.session.add(Review(pub_id=p.id, reviewer=current_user.username, rating=form_review.rating.data, review=form_review.review.data))
			db.session.commit()
			return redirect(url_for('users.visit_pub', p_id=p.id))
		if session['pull_from'] == 'owner' and p.owner.id == current_user.id:
			flash('Did you want to book from yourself ?', 'secondary')
			return redirect(url_for('users.visit_pub', p_id=p.id))
		if form_booking.validate():
			pass
		if p.bookable:
			res = current_user.reservations.filter_by(at_id=p.id).filter_by(cancelled=False).first()
			if res:
				flash(f'You already had reserved here for today.', 'secondary')
				flash(f'Reservation code : {res.id} -- Status : {"accepted" if res.confirmed else "waiting confirmation"}', f'{"success" if res.confirmed else "warning"}')
				return redirect(url_for('users.visit_pub', p_id=p.id))
			res = current_user.send_bookingReq(pub=p, guests=form_booking.guests.data)
			if res is not None:
				db.session.commit()
				flash(f'Reservation code : {res.id} -- Status : {"accepted" if res.confirmed else "waiting confirmation"}', f'{"success" if res.confirmed else "warning"}')
			else:
				flash(f'Reservation status : rejected due to no availability for {form_booking.guests.data} today', 'danger')
			return render_template('pub_page.html', pub=p, carousel=carousel, grid=grid,  paginate_rev=paginate_rev, reviews=paginate_rev.items, pull_from=session['pull_from'], form_review=form_review, form_booking=form_booking)
		flash("This pub can not accepts reservation on TeamPicks yet!", 'danger')
		return render_template('pub_page.html', pub=p, carousel=carousel, grid=grid,  paginate_rev=paginate_rev, reviews=paginate_rev.items, pull_from=session['pull_from'], form_review=form_review, form_booking=form_booking)
	form_booking.guests.data = '2'
	if session['pull_from'] == 'user':
		return render_template('pub_page.html', pub=p, carousel=carousel, grid=grid, paginate_rev=paginate_rev, reviews=paginate_rev.items, pull_from=session['pull_from'], form_review=form_review, form_booking=form_booking)
	return render_template('pub_page.html', pub=p, carousel=carousel, grid=grid, paginate_rev=paginate_rev, reviews=paginate_rev.items, pull_from=session['pull_from'], form_booking=form_booking)


@users.route('/<username>/manage-reservation/all', methods=['GET', 'POST'])
@login_required
def open_reservations_dashboard(username):
	page = request.args.get('page', 1, type=int)
	if session['pull_from'] == 'user':
		form = UpdateBookingReqForm()
		pagination = current_user.reservations.filter_by(cancelled=False).filter_by(confirmed=False).order_by(Reservation.date.desc()).paginate(page, per_page=6, error_out=False)
		return render_template('booking_manager.html', reservations=pagination.items, pagination=pagination, form=form, pull_from=session['pull_from'])
	else:
		pagination = current_user.pub.reservations.filter_by(cancelled=False).filter_by(confirmed=False).order_by(Reservation.date.desc()).paginate(page, per_page=12, error_out=False)
		return render_template('booking_manager.html', reservations=pagination.items, pagination=pagination, pull_from=session['pull_from'])


@users.route('/<username>/update-reservation/<int:res_id>%<guests>')
@login_required
def update_reservation(username, res_id, guests):
	r = Reservation.query.get(res_id)
	r.guests = guests
	db.session.commit()
	return redirect(url_for('users.open_reservations_dashboard', username=username))


@users.route('/<username>/cancel-reservation/<int:res_id>')
@login_required
def cancel_reservation(username, res_id):
	res = Reservation.query.get(res_id)
	res.cancelled = True
	db.session.commit()
	flash(f'Your reservation at {Pub.query.get(res.at_id).name} has been withdrawn successfully.', 'success')
	return redirect(url_for('users.open_reservations_dashboard', username=username))


@users.route('/<username>/accept-reservation/<int:res_id>')
@login_required
def accept_reservation(username, res_id):
	r = Reservation.query.get(res_id)
	r.confirmed = True
	if current_user.pub.is_available_for(r.guests):
		current_user.pub.book_for(r.guests)
		flash(f'Done! {r.by_id} will be soon notified about that.', 'success')
	else:
		r.queued = True
		flash(f'This reservation has been added to the queue because you only have {current_user.pub.get_availability()} seats left in the pub. ', 'warning')
	db.session.commit()
	return redirect(url_for('users.open_reservations_dashboard', username=username))

