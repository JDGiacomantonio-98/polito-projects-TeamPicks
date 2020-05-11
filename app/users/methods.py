import os
import secrets
from PIL import Image
from flask import current_app
from flask_login import current_user


def save_profilePic(imgFile):
    if imgFile:
        hexCode = secrets.token_hex(10)
        while hexCode in current_user.img:
            hexCode = secrets.token_hex(10)
        if ('def_' not in current_user.img) and (current_user.img != 'favicon.png'):
            sourcePath = os.path.join(current_app.root_path, 'static/profile_pics/users', current_user.img)
            try:
                os.remove(sourcePath)
            except FileNotFoundError:
                pass
        fileName, fileExt = os.path.splitext(imgFile.filename)
        fileName = hexCode + fileExt.lower()
        targetPath = os.path.join(current_app.root_path, 'static/profile_pics/users', fileName)
        imgFile = resizeTo(imgFile, size=250)
        imgFile.save(targetPath)
    else:
        fileName = current_user.img
    return fileName


def resizeTo(imgFile, size):
    resizedImg = Image.open(imgFile)
    resizedImg.thumbnail((size, size))
    return resizedImg
