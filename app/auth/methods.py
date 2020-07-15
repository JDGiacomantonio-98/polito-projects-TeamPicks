from flask import current_app, session
from itsdangerous import TimedJSONWebSignatureSerializer as timedTokenizer

from app import db, pswBurner
from app.dbModels import User, Owner


def hash_psw(psw):
	return pswBurner.generate_password_hash(psw).decode('utf-8')


def verify_psw(pswHash, psw):
	return pswBurner.check_password_hash(pswHash, psw)


def verify_token(token, to_confirm_account=False):
	try:
		user_id = timedTokenizer(current_app.config['SECRET_KEY']).loads(token)['load']
		if to_confirm_account:
			if session['pull_from'] == 'user':
				return User.query.get(user_id), user_id  # (!) FIX HERE : what if is not an User but a Pub ?
			return Owner.query.get(user_id), user_id
		else:
			if session['pull_from'] == 'user':
				return User.query.get(user_id), user_id  # (!) FIX HERE : what if is not an User but a Pub ?
			return Owner.query.get(user_id), user_id
	except:
		return None


def confirm_account(token):
	u, u_id = verify_token(token, to_confirm_account=True)
	if u_id == u.id:
		u.confirmed = True
		db.session.commit()
		return u
	else:
		u.confirmed = False
		db.session.commit()
		return None


def lock_account(user):
	user.acc_locked = True
	db.session.commit()