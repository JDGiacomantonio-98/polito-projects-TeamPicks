import os
import secrets
from PIL import Image
from flask import current_app
from flask_login import current_user


def save_profilePic(imgFile):
    if imgFile:
        hexCode = secrets.token_hex(6)
        while hexCode in current_user.img:
            hexCode = secrets.token_hex(6)
        if ('default_' not in current_user.img) and (current_user.img != 'favicon.png'):
            sourcePath = os.path.join(current_app.root_path, 'static/profile_pics/usersg', current_user.img)
            os.remove(sourcePath)
        fileName, fileExt = os.path.splitext(imgFile.filename)
        fileName = hexCode + fileExt.lower()
        targetPath = os.path.join(current_app.root_path, 'static/profile_pics/users', fileName)
        imgFile = resizeTo125(imgFile)
        imgFile.save(targetPath)
    else:
        fileName = current_user.img
    return fileName


def resizeTo125(imgFile):
    resizedImg = Image.open(imgFile)
    resizedImg.thumbnail((200, 200))
    return resizedImg
