from os import path, remove, listdir, rename

from flask import session
from flask_login import current_user
from PIL import Image

from app.main.methods import handle_userBin


def upload_profilePic(imgFile):
	if not imgFile:
		fileName = current_user.profile_img
		return fileName
	if current_user.profile_img not in ('def_', 'favicon'):
		bin_url = handle_userBin(current_user.get_file_address(), absolute_url=True)
		try:
			remove(f'{bin_url}{current_user.profile_img}')
		except FileNotFoundError:
			pass
		fileName, fileExt = path.splitext(imgFile.filename)
		if session['pull_from'] == 'user':
			fileName = f'U__{current_user.get_file_address()}{fileExt.lower()}'
		else:
			fileName = f'O__{current_user.get_file_address()}{fileExt.lower()}'
		imgFile = resize_to(imgFile, size=500)
		imgFile.save(f'{bin_url}{fileName}')
		return fileName


def upload_carousel(files):
	if files is None:
		return
	bin_url = handle_userBin(current_user.get_file_address(), absolute_url=True)
	bin_f = listdir(bin_url)
	if len(bin_f) + len(files) > 9:
		for i in range(len(bin_f)-1, len(bin_f) - len(files) - 2, -1):
			if not (('U__' in bin_f[i]) or ('O__' in bin_f[i])):
				try:
					remove(f'{bin_url}{bin_f[i]}')
				except FileNotFoundError:
					pass
		bin_f = listdir(bin_url)
	for i in range(len(bin_f) - 1, -1, -1):
		if not (('U__' in bin_f[i]) or ('O__' in bin_f[i])):
			f_n = bin_f[i].split('__')
			rename(f'{bin_url}{bin_f[i]}', f'{bin_url}{int(f_n[0])+len(files)}__{f_n[1]}')
	i = 0
	for img in files:
		i += 1
		fileName, fileExt = path.splitext(img.filename)
		fileName = f'{i}__{current_user.get_file_address()}{fileExt.lower()}'
		img = resize_to(img, size=500)
		img.save(f'{bin_url}{fileName}')
	return


def resize_to(imgFile, size):
	resizedImg = Image.open(imgFile)
	resizedImg.thumbnail((size, size))
	return resizedImg
