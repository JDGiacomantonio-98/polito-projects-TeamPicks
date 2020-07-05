from os import path, remove
from secrets import token_hex

from flask import current_app
from flask_login import current_user
from itsdangerous import TimedJSONWebSignatureSerializer as timedTokenizer
from PIL import Image

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
			return User.query.get(user_id), user_id  # (!) FIX HERE : what if is not an User but a Pub ?
		else:
			return User.query.get(user_id)  # (!) FIX HERE : what if is not an User but a Pub ?
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


def save_profilePic(imgFile):
	if imgFile:
		hexCode = token_hex(10)
		while hexCode in current_user.img:
			hexCode = token_hex(10)
		if ('def_' not in current_user.img) and (current_user.img != 'favicon.png'):
			sourcePath = path.join(current_app.root_path, 'static/profile_pics/users', current_user.img)
			try:
				remove(sourcePath)
			except FileNotFoundError:
				pass
		fileName, fileExt = path.splitext(imgFile.filename)
		fileName = hexCode + fileExt.lower()
		targetPath = path.join(current_app.root_path, 'static/profile_pics/users', fileName)
		imgFile = resize_to(imgFile, size=250)
		imgFile.save(targetPath)
	else:
		fileName = current_user.img
	return fileName


def resize_to(imgFile, size):
	resizedImg = Image.open(imgFile)
	resizedImg.thumbnail((size, size))
	return resizedImg
