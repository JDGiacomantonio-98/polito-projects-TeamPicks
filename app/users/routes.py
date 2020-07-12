from datetime import datetime
from shutil import rmtree
from string import capwords

from flask import render_template, url_for, flash, redirect, request, abort, make_response, session, g
from flask_login import logout_user, login_required, current_user

from app.users.methods import upload_profilePic, upload_carousel
from app.auth.methods import lock_account
from app.users.forms import ProfileDashboardForm, UploadProfileImgForm, CreateGroupForm, SearchItemsForm, DeleteAccountForm, UploadProfileCarouselForm
from app.users import users
from app.main.methods import send_confirmation_email, handle_userBin
from app.main.forms import TryAppForm
from app import db
from app.dbModels import User, Owner, Group, Pub


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
	if request.method == 'POST':
		if form.validate_on_submit():
			u = User.query.filter_by(username=form.searchedItem.data).first_or_404()
			return redirect(url_for('users.profile', username=u.username))
			# return render_template('search_pub.html')
		return redirect(url_for('users.home', username=current_user.username))
	return render_template('home.html', form=form, title='home')


@users.route('/<username>/profile-dashboard', methods=['GET', 'POST'])
@login_required
def profile(username):
	pr_u = User.query.filter_by(username=username).first()
	form_img = UploadProfileImgForm()
	form_carousel = UploadProfileCarouselForm()
	if current_user.id == pr_u.id:
		form_info = ProfileDashboardForm()
		if request.method == 'POST':
			if form_img.upload_img.data:
				if form_img.validate():
					current_user.profile_img = upload_profilePic(form_img.img.data)
					db.session.commit()
					flash('You profile has been updated!', 'success')
					return redirect(url_for('users.profile', username=current_user.username))
				flash('There are some problem with your input: please make correction before resubmitting !', 'danger')
				return render_template('profile.html', title=f'{current_user.firstName} {current_user.lastName}',
									   is_viewer=(current_user.id != pr_u.id), user=pr_u, imgFile=pr_u.get_imgFile(),
									   carousel=current_user.get_imgCarousel(), form_info=form_info, form_img=form_img, groups=pr_u.groups.count())
			if form_img.modify_about_me.data:
				if form_img.validate():
					current_user.about_me = form_img.about_me.data
					db.session.commit()
					flash('You profile has been updated!', 'success')
					return redirect(url_for('users.profile', username=current_user.username))
				flash('There are some problem with your input: please make correction before resubmitting !', 'danger')
				return render_template('profile.html', title=f'{current_user.firstName} {current_user.lastName}',
									   is_viewer=(current_user.id != pr_u.id), user=pr_u, imgFile=pr_u.get_imgFile(),
									   carousel=current_user.get_imgCarousel(), form_info=form_info, form_img=form_img, groups=pr_u.groups.count())
			if form_info.submit.data:
				if form_info.validate():
					if current_user.email != form_info.email.data:
						current_user.confirmed = False
						current_user.email = form_info.email.data
						send_confirmation_email(recipient=current_user, flash_msg=True)
					current_user.firstName = form_info.firstName.data
					current_user.lastName = form_info.lastName.data
					current_user.username = form_info.username.data
					db.session.commit()
					flash('You profile has been updated!', 'success')
					return redirect(url_for('users.profile', username=current_user.username))
				flash('There are some problem with your input: please make correction before resubmitting !', 'danger')
				form_img.about_me.data = current_user.about_me
				return render_template('profile.html', title=f'{current_user.firstName} {current_user.lastName}',
									   is_viewer=(current_user.id != pr_u.id), user=pr_u, imgFile=pr_u.get_imgFile(),
									   carousel=pr_u.get_imgCarousel(), form_info=form_info, form_img=form_img, form_carousel=form_carousel, groups=pr_u.groups.count())
			if form_carousel.upload_carousel.data:
				if form_carousel.validate():
					upload_carousel(form_carousel.images.data)
					flash('You profile has been updated!', 'success')
					return redirect(url_for('users.profile', username=current_user.username))
		form_info.firstName.data = capwords(current_user.firstName)
		form_info.lastName.data = capwords(current_user.lastName)
		form_info.username.data = current_user.username
		form_info.email.data = current_user.email
		form_img.about_me.data = current_user.about_me.capitalize()
		resp = make_response(render_template('profile.html', title=f'{current_user.firstName} {current_user.lastName}',
											 is_viewer=(current_user.id != pr_u.id), user=pr_u, imgFile=pr_u.get_imgFile(),
											 carousel=pr_u.get_imgCarousel(), form_info=form_info, form_img=form_img, form_carousel=form_carousel, groups=pr_u.groups.count()))
		resp.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
		resp.headers['Cache-Control'] = 'public, max-age=0'
		return resp
	if current_user.confirmed:
		form_img.about_me.data = pr_u.about_me
		# if 'user' == session.get('pull_from'):
		# 	form.firstName.data = pr_u.firstName
		# 	form.lastName.data = pr_u.lastName
		# 	form.username.data = pr_u.username
		# 	form.email.data = pr_u.email
		return render_template('profile.html', title=f'{current_user.firstName} {current_user.lastName}',
							   is_viewer=(current_user.id != pr_u.id), user=pr_u, imgFile=pr_u.get_imgFile(),
							   carousel=pr_u.get_imgCarousel(), form_img=form_img, form_carousel=form_carousel, groups=pr_u.groups.count())
		# else:
		# 	return render_template('errors/wip.html', title='coming soon!')
	flash('Your profile has been temporally deactivated until you reconfirm it.', 'secondary')
	return render_template('profile.html', title=f'{current_user.firstName} {current_user.lastName}',
						   is_viewer=(current_user.id != pr_u.id), user=pr_u, imgFile=pr_u.get_imgFile(),
						   carousel=pr_u.get_imgCarousel(), form_img=form_img, form_carousel=form_carousel, groups=pr_u.groups.count())


@users.route('/delete/<u_id>', methods=['GET', 'POST'])
@login_required
def delete_account(u_id, ATTEMPTS=3):
	if int(u_id) == current_user.id: 	# deletion is authorized only by code and not by manual writing the URL
		if not current_user.is_acc_locked():
			form = DeleteAccountForm()
			if request.method == 'POST':
				session['del-attempt'] += 1
				if form.validate_on_submit():
					rmtree(handle_userBin(current_user.get_file_address()))
					db.session.delete(current_user)
					db.session.commit()
					logout_user()
					flash('Your account has been successfully removed. We are sad about that :C', 'secondary')
					session.clear()
					return redirect(url_for('main.index'))
				if ATTEMPTS - session['del-attempt'] != 0:
					flash(f'{ATTEMPTS - session["del-attempt"]} attempts remaining', 'danger')
					return render_template('delete_account.html', form=form, title=':C')
				lock_account(current_user)
				logout_user()
				# notify teampicks staff by email
				flash('Your account has been temporarly locked because the system detected a brutal attempt to delete it.\nTeampicks has been notified about that.', 'danger')
				return redirect(url_for('main.index'))
			try:
				session['del-attempt']
			except KeyError:
				session['del-attempt'] = 0
			return render_template('delete_account.html', form=form, title=':C')
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
	return render_template('create_group.html', form=form, title='your new group')


@users.route('/pub/<int:p_id>')
@login_required
def visit_pub_profile(p_id):
	p = Pub.query.get(p_id)
	return render_template('pub_page.html', pub=p)


@users.route('/find-pubs')
@login_required
def search_pub():
	return render_template('search_pub.html', pubs=Pub.query.filter(Pub.owner.has(city=current_user.city)).all())
