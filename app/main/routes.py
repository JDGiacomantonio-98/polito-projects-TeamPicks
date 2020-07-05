from datetime import datetime

from flask import render_template, url_for, redirect, request
from flask_login import login_required, current_user

from app.main import main
from app.main.forms import TryAppForm
from app.main.methods import send_confirmation_email
from app.dbModels import Owner


@main.route('/', methods=['GET', 'POST'])
def index():
	if current_user.is_anonymous:
		form = TryAppForm()
		if request.method == 'POST':
			pubs = Owner.query.filter_by(city=form.city.data).count()
			return render_template('landing.html', city=form.city.data, pubs=pubs)
		return render_template('landing.html', form=form, time=datetime.utcnow())
	return redirect(url_for('users.home', username=current_user.username))


@main.route('/pricing')
def show_pricing():
	return render_template('pricing.html', title='Pricing')


@main.route('/find-a-pub')
def find_pub():
	return render_template('find_pub.html')


@main.route('/<callerRoute>/acc-confirmation')
@login_required
def send_confirmation(callerRoute):
	send_confirmation_email(recipient=current_user)
	if callerRoute == 'profile':
		return redirect(url_for('users.openProfile', userInfo=current_user.username))


@main.route('/search/<query_obj>')
def display_search_results(query_obj):
	pass


@main.route('/contacts')
def contact():
	return render_template('contact_us.html', title='Let Us Know!', heading='We love to hear from you.')


@main.route('/<callerPage>/work-in-progress')
def show_wip(callerPage):
	return render_template('errors/wip.html')

