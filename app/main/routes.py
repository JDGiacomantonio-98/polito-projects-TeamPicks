from datetime import datetime

from flask import render_template, url_for, redirect, request, flash, session, abort, current_app
from flask_login import login_required, current_user

from app.main import main
from app.main.forms import TryAppForm
from app.main.methods import send_confirmation_email
from app.dbModels import Owner, Reservation
from app import db


@main.route('/', methods=['GET', 'POST'])
def index():
	if current_user.is_anonymous:
		form = TryAppForm()
		if request.method == 'POST' and form.submit.data:
			pubs = Owner.query.filter_by(city=form.city.data).count()
			return render_template('landing.html', city=form.city.data.lower(), pubs=pubs, title='Join us!')
		return render_template('landing.html', form=form, time=datetime.utcnow())
	return redirect(url_for('users.home', username=current_user.username))


@main.route('/pricing')
def show_pricing():
	return render_template('pricing.html', title='Pricing')


@main.route('/email-confirmation')
@login_required
def send_email_confirmation():
	send_confirmation_email(recipient=current_user, pull_from=session['pull_from'], email_update=True)
	flash('A new confirmation email has been sent to your inbox.', 'info')
	return redirect(url_for('users.profile', username=current_user.username))


@main.route('/reservation-cleanup')
def delete_reservations():
	if current_user.email != current_app.config['FLASKY_ADMIN']:
		flash('This page is admins reserved only.', 'warning')
		abort(403)
	res = Reservation.query.filter_by(cancelled=True).all()
	for r in res:
		db.session.delete(r)
		db.session.commit()
	flash(f'DONE. Reservation dropped : {len(res)}', 'danger')
	return render_template('admin_dashboard.html', pull_from=session['pull_from'])


@main.route('/contacts')
def contact_us():
	return render_template('contact_us.html', title='Let Us Know!', heading='We love to hear from you.')

