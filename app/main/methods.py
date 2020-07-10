from os import path, mkdir, getcwd
from threading import Thread

from flask import render_template, current_app, flash
from flask_mail import Message

from app import mail
from app.dbModels import User, Owner


def handle_userBin(hex_address):
	url = f'{current_app.config["USERS_UPLOADS_BIN"]}\\{hex_address}'
	if not path.isdir(url):
		try:
			mkdir(url)
		except OSError as e:
			print(e)
	return f'{url}\\'


def find_user(credential, email_only=False):
	if email_only:
		u = (User.query.filter_by(email=credential).first())
		pull_from = 'user'
		if not u:
			u = (Owner.query.filter_by(email=credential).first())
			pull_from = 'owner'
	else:
		u = (User.query.filter_by(email=credential).first() or User.query.filter_by(username=credential).first())
		pull_from = 'user'
		if not u:
			u = (Owner.query.filter_by(email=credential).first() or Owner.query.filter_by(username=credential).first())
			pull_from = 'owner'
	return u, pull_from


def cherryPick_user(pull_from, u_id):
	if pull_from == 'user':
		u = User.query.get(u_id)
	else:
		u = Owner.query.get(u_id)
	return u, pull_from


def check_subs_payment(owner):
	# draft of a very complex func
	# check things related with subs payment
	all_ok = True

	if all_ok:
		return True
	else:
		# notify owner his payment is overdue and block his account
		pass


def send_on_thread(app, msg):
	with app.app_context():
		mail.send(msg)


def send_email(recipient, templatePath=None, mailTitle=None, token=None, background=True):
	msg = Message('TeamPicks Account -- ' + mailTitle.upper(),
				  sender='teampicks.help@gmail.com',
				  recipients=[recipient.email])
	if token:
		msg.body = render_template(templatePath + '.txt', token=token, user=recipient)
	else:
		msg.body = render_template(templatePath + '.txt', user=recipient)
	# _external parameter generate an absolute URL whose works outside app environment
	if background:
		Thread(target=send_on_thread, args=(current_app._get_current_object(), msg)).start()
	else:
		mail.send(msg)


def send_confirmation_email(recipient, email_update=False, flash_msg=False, background=True):
	if email_update:
		msg = Message('TeamPicks Account -- EMAIL UPDATE',
					  sender='teampicks.help@gmail.com',
					  recipients=[recipient.email])
	else:
		msg = Message('TeamPicks Account -- ACCOUNT CONFIRMATION',
					  sender='teampicks.help@gmail.com',
					  recipients=[recipient.email])
	msg.body = render_template('email-copy/confirm-registration.txt', email_update=email_update, token=recipient.create_token(), user=recipient)
	if background:
		Thread(target=send_on_thread, args=(current_app._get_current_object(), msg)).start()
	else:
		mail.send(msg)
	if flash_msg:
		flash('A confirmation email has been sent to you. Open your inbox!', 'warning')


def send_pswReset_email(recipient, flash_msg=False, background=True):
	msg = Message('TeamPicks Account -- PASSWORD RESET',
				  sender='teampicks.help@gmail.com',
				  recipients=[recipient.email])
	msg.body = render_template('email-copy/reset-psw.txt', token=recipient.create_token(), user=recipient)
	if background:
		Thread(target=send_on_thread, args=(current_app._get_current_object(), msg)).start()
	else:
		mail.send(msg)
	if flash_msg:
		flash('A confirmation email has been sent to you. Open your inbox!', 'warning')
