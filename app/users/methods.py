from os import path, remove


from flask import current_app
from flask_login import current_user
from PIL import Image

from app.main.methods import handle_userBin


def upload_profilePic(imgFile):
	if not imgFile:
		fileName = current_user.profile_img
		return fileName
	if current_user.profile_img not in ('def_', 'favicon'):
		w_url = handle_userBin(current_user.get_file_address())
		try:
			remove(f'{w_url}{current_user.profile_img}')
		except FileNotFoundError:
			pass
	fileName, fileExt = path.splitext(imgFile.filename)
	fileName = f'p_{current_user.get_file_address()}{fileExt.lower()}'
	imgFile = resize_to(imgFile, size=250)
	imgFile.save(f'{w_url}{fileName}')
	return fileName


def resize_to(imgFile, size):
	resizedImg = Image.open(imgFile)
	resizedImg.thumbnail((size, size))
	return resizedImg
